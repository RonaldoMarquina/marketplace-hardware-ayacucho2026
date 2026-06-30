from io import BytesIO
from pathlib import Path

import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.anuncio import Anuncio
from app.models.media_anuncio import MediaAnuncio
from app.models.usuario import Usuario


PASSWORD = "123456#P"
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde"
)
WEBP_BYTES = b"RIFF\x10\x00\x00\x00WEBPVP8 "
MP4_BYTES = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42"


def crear_usuario(correo="editor@gmail.com", rol="USER_ESTANDAR"):
    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")
    usuario = Usuario(
        nombre=f"Usuario {correo}",
        correo=correo,
        password_hash=password_hash,
        telefono=f"9{abs(hash(correo)) % 100000000:08d}",
        rol=rol,
        estado="ACTIVO",
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def crear_anuncio(usuario, **overrides):
    anuncio = Anuncio(
        usuario_id=usuario.id,
        titulo="Ryzen 5 5600X",
        descripcion="Descripcion inicial",
        categoria="COMPONENTES",
        subcategoria="PROCESADOR",
        condicion="USADO",
        precio="350.00",
        especificaciones={
            "socket": "AM4",
            "nucleos": 6,
            "cooler": True,
        },
        estado="ACTIVO",
        reactivaciones_count=0,
    )
    for campo, valor in overrides.items():
        setattr(anuncio, campo, valor)
    db.session.add(anuncio)
    db.session.commit()
    return anuncio


def token_para(usuario):
    return create_access_token(
        identity=str(usuario.id),
        additional_claims={"correo": usuario.correo, "rol": usuario.rol},
    )


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def media_file(content, filename):
    return (BytesIO(content), filename)


def crear_media(anuncio, upload_folder, tipo_media="imagen", nombre="archivo.png", es_principal=False, orden=None):
    relative_path = f"uploads/anuncios/{anuncio.id}/{nombre}"
    absolute_path = Path(upload_folder) / "anuncios" / str(anuncio.id) / nombre
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_bytes(PNG_BYTES if tipo_media == "imagen" else MP4_BYTES)

    media = MediaAnuncio(
        anuncio_id=anuncio.id,
        tipo_media=tipo_media,
        ruta_relativa=relative_path,
        es_principal=es_principal,
        orden=orden,
    )
    db.session.add(media)
    db.session.commit()
    return media, absolute_path


def test_editar_anuncio_aplica_merge_patch_e_ignora_campos_inmutables(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        anuncio_id = anuncio.id
        usuario_id = usuario.id

    response = client.patch(
        f"/api/v1/anuncios/{anuncio_id}",
        json={
            "titulo": "Ryzen 5 5600X rebajado",
            "descripcion": "Precio rebajado, negociable",
            "usuario_id": 999,
            "estado": "INACTIVO",
            "especificaciones": {
                "cooler": None,
                "velocidad_base_ghz": 3.7,
            },
        },
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["titulo"] == "Ryzen 5 5600X rebajado"
    assert body["data"]["descripcion"] == "Precio rebajado, negociable"
    assert body["data"]["estado"] == "ACTIVO"
    assert body["data"]["especificaciones"]["socket"] == "AM4"
    assert "cooler" not in body["data"]["especificaciones"]
    assert body["data"]["especificaciones"]["velocidad_base_ghz"] == 3.7

    with app.app_context():
        anuncio_db = db.session.get(Anuncio, anuncio_id)
        assert anuncio_db.usuario_id == usuario_id
        assert anuncio_db.estado == "ACTIVO"
        assert anuncio_db.especificaciones == {
            "socket": "AM4",
            "nucleos": 6,
            "velocidad_base_ghz": 3.7,
        }


def test_editar_anuncio_categoria_sin_subcategoria_retorna_422(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.patch(
        f"/api/v1/anuncios/{anuncio_id}",
        json={"categoria": "REDES"},
        headers=headers(token),
    )

    assert response.status_code == 422
    body = response.get_json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "subcategoria" in body["data"]


def test_marcar_anuncio_vendido_exitoso(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.patch(
        f"/api/v1/anuncios/{anuncio_id}/vendido",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["estado"] == "VENDIDO"
    assert "vendido" in body["message"].lower()


def test_marcar_anuncio_vendido_desde_inactivo_retorna_409(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario, estado="INACTIVO")
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.patch(
        f"/api/v1/anuncios/{anuncio_id}/vendido",
        headers=headers(token),
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "CONFLICT"


def test_desactivar_y_reactivar_anuncio_actualiza_estado_y_limite(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario, estado="INACTIVO", reactivaciones_count=2)
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.patch(
        f"/api/v1/anuncios/{anuncio_id}/reactivar",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["estado"] == "ACTIVO"
    assert body["data"]["reactivaciones_count"] == 3
    assert body["data"]["reactivaciones_restantes"] == 0

    response_limite = client.patch(
        f"/api/v1/anuncios/{anuncio_id}/desactivar",
        headers=headers(token),
    )
    assert response_limite.status_code == 200

    response_forbidden = client.patch(
        f"/api/v1/anuncios/{anuncio_id}/reactivar",
        headers=headers(token),
    )
    assert response_forbidden.status_code == 403
    assert response_forbidden.get_json()["error"] == "FORBIDDEN"


def test_reactivar_anuncio_user_estandar_limite_25_activos_retorna_403(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio_inactivo = crear_anuncio(usuario, estado="INACTIVO")
        for i in range(25):
            db.session.add(Anuncio(
                usuario_id=usuario.id,
                titulo=f"Activo {i}",
                descripcion="Descripcion",
                categoria="COMPONENTES",
                subcategoria="PROCESADOR",
                condicion="USADO",
                precio="100.00",
                estado="ACTIVO",
                reactivaciones_count=0,
            ))
        db.session.commit()
        token = token_para(usuario)
        anuncio_id = anuncio_inactivo.id

    response = client.patch(
        f"/api/v1/anuncios/{anuncio_id}/reactivar",
        headers=headers(token),
    )

    assert response.status_code == 403
    body = response.get_json()
    assert body["error"] == "FORBIDDEN"
    assert "25 anuncios activos" in body["message"]


def test_reactivar_anuncio_tienda_verificada_sin_limite_25(client, app):
    with app.app_context():
        usuario = crear_usuario(correo="tienda@gmail.com", rol="TIENDA_VERIFICADA")
        anuncio_inactivo = crear_anuncio(usuario, estado="INACTIVO")
        for i in range(25):
            db.session.add(Anuncio(
                usuario_id=usuario.id,
                titulo=f"Activo tienda {i}",
                descripcion="Descripcion",
                categoria="COMPONENTES",
                subcategoria="PROCESADOR",
                condicion="USADO",
                precio="100.00",
                estado="ACTIVO",
                reactivaciones_count=0,
            ))
        db.session.commit()
        token = token_para(usuario)
        anuncio_id = anuncio_inactivo.id

    response = client.patch(
        f"/api/v1/anuncios/{anuncio_id}/reactivar",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["estado"] == "ACTIVO"


def test_reordenar_media_actualiza_principal_y_orden(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        media_1, _ = crear_media(anuncio, app.config["UPLOAD_FOLDER"], nombre="1.png", es_principal=True, orden=0)
        media_2, _ = crear_media(anuncio, app.config["UPLOAD_FOLDER"], nombre="2.png", es_principal=False, orden=1)
        media_3, _ = crear_media(anuncio, app.config["UPLOAD_FOLDER"], nombre="3.png", es_principal=False, orden=2)
        anuncio_id = anuncio.id
        media_1_id = media_1.id
        media_2_id = media_2.id
        media_3_id = media_3.id

    response = client.patch(
        f"/api/v1/anuncios/{anuncio_id}/media/orden",
        json={"orden": [media_3_id, media_1_id, media_2_id]},
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert [item["id"] for item in body["data"]["media"]] == [media_3_id, media_1_id, media_2_id]
    assert body["data"]["media"][0]["es_principal"] is True
    assert body["data"]["media"][0]["orden"] == 0
    assert body["data"]["media"][1]["orden"] == 1


def test_reordenar_media_con_video_en_array_retorna_422(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        media_1, _ = crear_media(anuncio, app.config["UPLOAD_FOLDER"], nombre="1.png", es_principal=True, orden=0)
        media_2, _ = crear_media(anuncio, app.config["UPLOAD_FOLDER"], nombre="2.png", es_principal=False, orden=1)
        video, _ = crear_media(anuncio, app.config["UPLOAD_FOLDER"], tipo_media="video", nombre="demo.mp4")
        anuncio_id = anuncio.id
        media_1_id = media_1.id
        media_2_id = media_2.id
        video_id = video.id

    response = client.patch(
        f"/api/v1/anuncios/{anuncio_id}/media/orden",
        json={"orden": [media_1_id, video_id, media_2_id]},
        headers=headers(token),
    )

    assert response.status_code == 422
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_eliminar_imagen_principal_promueve_siguiente_y_borra_archivo(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        principal, principal_path = crear_media(
            anuncio,
            app.config["UPLOAD_FOLDER"],
            nombre="principal.png",
            es_principal=True,
            orden=0,
        )
        secundaria, secondary_path = crear_media(
            anuncio,
            app.config["UPLOAD_FOLDER"],
            nombre="secundaria.png",
            es_principal=False,
            orden=1,
        )
        anuncio_id = anuncio.id
        principal_id = principal.id
        secundaria_id = secundaria.id

    assert principal_path.exists() is True
    assert secondary_path.exists() is True

    response = client.delete(
        f"/api/v1/anuncios/{anuncio_id}/media/{principal_id}",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["eliminado"] == {"id": principal_id, "tipo_media": "imagen"}
    assert len(body["data"]["media_restante"]) == 1
    assert body["data"]["media_restante"][0]["id"] == secundaria_id
    assert body["data"]["media_restante"][0]["es_principal"] is True
    assert body["data"]["media_restante"][0]["orden"] == 0
    assert principal_path.exists() is False


def test_reemplazar_media_actualiza_ruta_y_elimina_archivo_anterior(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        media, old_path = crear_media(
            anuncio,
            app.config["UPLOAD_FOLDER"],
            nombre="vieja.png",
            es_principal=True,
            orden=0,
        )
        anuncio_id = anuncio.id
        media_id = media.id
        old_relative_path = media.ruta_relativa

    response = client.put(
        f"/api/v1/anuncios/{anuncio_id}/media/{media_id}",
        data={"media": media_file(WEBP_BYTES, "nueva.webp")},
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["id"] == media_id
    assert body["data"]["tipo_media"] == "imagen"
    assert body["data"]["ruta_relativa"] != old_relative_path
    assert old_path.exists() is False

    with app.app_context():
        media_db = db.session.get(MediaAnuncio, media_id)
        assert media_db.ruta_relativa == body["data"]["ruta_relativa"]


def test_reemplazar_media_con_tipo_distinto_retorna_422(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        media, _ = crear_media(
            anuncio,
            app.config["UPLOAD_FOLDER"],
            tipo_media="video",
            nombre="demo.mp4",
            es_principal=False,
            orden=None,
        )
        anuncio_id = anuncio.id
        media_id = media.id

    response = client.put(
        f"/api/v1/anuncios/{anuncio_id}/media/{media_id}",
        data={"media": media_file(PNG_BYTES, "foto.png")},
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 422
    assert response.get_json()["error"] == "INVALID_FILE_TYPE"
