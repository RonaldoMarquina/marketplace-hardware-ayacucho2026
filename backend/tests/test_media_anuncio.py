from io import BytesIO

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


def _telefono_para(correo):
    base = abs(hash(correo)) % 100000000
    return f"9{base:08d}"


def crear_usuario(correo="vendedor_media@gmail.com"):
    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")
    usuario = Usuario(
        nombre=f"Usuario {correo}",
        correo=correo,
        password_hash=password_hash,
        telefono=_telefono_para(correo),
        rol="USER_ESTANDAR",
        estado="ACTIVO",
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def crear_anuncio(usuario):
    anuncio = Anuncio(
        usuario_id=usuario.id,
        titulo="Ryzen 5",
        descripcion="Descripcion",
        categoria="COMPONENTES",
        subcategoria="PROCESADOR",
        condicion="USADO",
        precio="100.00",
        estado="ACTIVO",
    )
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


def media_url(anuncio_id):
    return f"/api/v1/anuncios/{anuncio_id}/media"


def file_tuple(content, filename):
    return (BytesIO(content), filename)


def test_subir_imagen_y_video_exitoso(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.post(
        media_url(anuncio_id),
        data={
            "media": [
                file_tuple(PNG_BYTES, "foto.png"),
                file_tuple(MP4_BYTES, "demo.mp4"),
            ]
        },
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]["media"]) == 2
    assert body["data"]["media"][0]["tipo_media"] == "imagen"
    assert body["data"]["media"][0]["es_principal"] is True
    assert body["data"]["media"][0]["orden"] == 0
    assert body["data"]["media"][1]["tipo_media"] == "video"
    assert body["data"]["media"][1]["orden"] is None

    with app.app_context():
        assert MediaAnuncio.query.count() == 2


def test_subir_media_sin_jwt_retorna_401(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        anuncio_id = anuncio.id

    response = client.post(
        media_url(anuncio_id),
        data={"media": [file_tuple(PNG_BYTES, "foto.png")]},
        content_type="multipart/form-data",
    )

    assert response.status_code == 401


def test_subir_media_anuncio_ajeno_retorna_403(client, app):
    with app.app_context():
        propietario = crear_usuario("propietario@gmail.com")
        intruso = crear_usuario("intruso@gmail.com")
        anuncio = crear_anuncio(propietario)
        token = token_para(intruso)
        anuncio_id = anuncio.id

    response = client.post(
        media_url(anuncio_id),
        data={"media": [file_tuple(PNG_BYTES, "foto.png")]},
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_subir_media_anuncio_inexistente_retorna_404(client, app):
    with app.app_context():
        usuario = crear_usuario()
        token = token_para(usuario)

    response = client.post(
        media_url(9999),
        data={"media": [file_tuple(PNG_BYTES, "foto.png")]},
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 404


def test_subir_media_sin_archivos_retorna_400(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.post(
        media_url(anuncio_id),
        data={},
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "MISSING_FILE"


def test_subir_gif_retorna_422(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.post(
        media_url(anuncio_id),
        data={"media": [file_tuple(b"GIF89a", "animacion.gif")]},
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 422
    assert response.get_json()["error"] == "INVALID_FILE_TYPE"


def test_subir_mas_de_8_imagenes_total_retorna_409(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        for i in range(8):
            db.session.add(MediaAnuncio(
                anuncio_id=anuncio.id,
                tipo_media="imagen",
                ruta_relativa=f"uploads/anuncios/{anuncio.id}/{i}.png",
                es_principal=i == 0,
                orden=i,
            ))
        db.session.commit()
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.post(
        media_url(anuncio_id),
        data={"media": [file_tuple(PNG_BYTES, "extra.png")]},
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "CONFLICT"


def test_subir_segundo_video_retorna_409(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        db.session.add(MediaAnuncio(
            anuncio_id=anuncio.id,
            tipo_media="video",
            ruta_relativa=f"uploads/anuncios/{anuncio.id}/demo.mp4",
            es_principal=False,
            orden=None,
        ))
        db.session.commit()
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.post(
        media_url(anuncio_id),
        data={"media": [file_tuple(MP4_BYTES, "otro.mp4")]},
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "CONFLICT"


def test_subir_mas_de_8_imagenes_en_peticion_retorna_422(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        anuncio_id = anuncio.id

    files = [file_tuple(PNG_BYTES, f"foto{i}.png") for i in range(9)]
    response = client.post(
        media_url(anuncio_id),
        data={"media": files},
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 422
    assert response.get_json()["error"] == "TOO_MANY_FILES"


def test_subir_imagen_mayor_a_10mb_retorna_413(client, app):
    with app.app_context():
        usuario = crear_usuario()
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        anuncio_id = anuncio.id

    archivo_grande = PNG_BYTES + (b"0" * (10 * 1024 * 1024 + 1))
    response = client.post(
        media_url(anuncio_id),
        data={"media": [file_tuple(archivo_grande, "grande.png")]},
        content_type="multipart/form-data",
        headers=headers(token),
    )

    assert response.status_code == 413
    assert response.get_json()["error"] == "FILE_TOO_LARGE"


