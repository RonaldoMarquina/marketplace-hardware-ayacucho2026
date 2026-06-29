import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.anuncio import Anuncio
from app.models.usuario import Usuario


PUBLICAR_URL = "/api/v1/anuncios"
PASSWORD = "123456#P"


def crear_usuario(correo="vendedor@gmail.com", rol="USER_ESTANDAR", estado="ACTIVO"):
    password_hash = bcrypt.hashpw(
        PASSWORD.encode("utf-8"),
        bcrypt.gensalt(rounds=10),
    ).decode("utf-8")
    usuario = Usuario(
        nombre=f"Vendedor {correo}",
        correo=correo,
        password_hash=password_hash,
        telefono="987654321",
        rol=rol,
        estado=estado,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def token_para_usuario(usuario):
    return create_access_token(
        identity=str(usuario.id),
        additional_claims={"correo": usuario.correo, "rol": usuario.rol},
    )


def headers_auth(token):
    return {"Authorization": f"Bearer {token}"}


def datos_anuncio(**overrides):
    data = {
        "titulo": "Ryzen 5 5600X casi nuevo",
        "categoria": "COMPONENTES",
        "subcategoria": "PROCESADOR",
        "condicion": "COMO_NUEVO",
        "precio": "450.00",
        "descripcion": "Procesador en excelente estado, incluye cooler.",
        "especificaciones": {
            "socket": "AM4",
            "nucleos": 6,
            "velocidad_base_ghz": 3.7,
            "incluye_cooler": True,
        },
    }
    data.update(overrides)
    return data


def test_publicar_anuncio_exitoso_retorna_201(client, app):
    with app.app_context():
        usuario = crear_usuario()
        token = token_para_usuario(usuario)

    response = client.post(
        PUBLICAR_URL,
        json=datos_anuncio(),
        headers=headers_auth(token),
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["titulo"] == "Ryzen 5 5600X casi nuevo"
    assert body["data"]["categoria"] == "COMPONENTES"
    assert body["data"]["subcategoria"] == "PROCESADOR"
    assert body["data"]["condicion"] == "COMO_NUEVO"
    assert body["data"]["estado"] == "ACTIVO"
    assert body["data"]["usuario_id"] is not None

    with app.app_context():
        anuncio = Anuncio.query.first()
        assert anuncio is not None
        assert anuncio.estado == "ACTIVO"
        assert anuncio.usuario.estado == "ACTIVO"
        assert anuncio.subcategoria == "PROCESADOR"
        assert anuncio.especificaciones["socket"] == "AM4"
        assert "tipo_componente" not in anuncio.especificaciones


def test_publicar_anuncio_sin_jwt_retorna_401(client):
    response = client.post(PUBLICAR_URL, json=datos_anuncio())

    assert response.status_code == 401
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "UNAUTHORIZED"


def test_publicar_anuncio_usuario_pendiente_retorna_403(client, app):
    with app.app_context():
        usuario = crear_usuario(estado="PENDIENTE_VERIFICACION")
        token = token_para_usuario(usuario)

    response = client.post(
        PUBLICAR_URL,
        json=datos_anuncio(),
        headers=headers_auth(token),
    )

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "FORBIDDEN"


def test_publicar_anuncio_categoria_invalida_retorna_422(client, app):
    with app.app_context():
        usuario = crear_usuario()
        token = token_para_usuario(usuario)

    response = client.post(
        PUBLICAR_URL,
        json=datos_anuncio(categoria="NO_EXISTE"),
        headers=headers_auth(token),
    )

    assert response.status_code == 422
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "VALIDATION_ERROR"
    assert "categoria" in body["data"]


def test_publicar_anuncio_subcategoria_invalida_retorna_422(client, app):
    with app.app_context():
        usuario = crear_usuario()
        token = token_para_usuario(usuario)

    response = client.post(
        PUBLICAR_URL,
        json=datos_anuncio(subcategoria="ROUTER"),
        headers=headers_auth(token),
    )

    assert response.status_code == 422
    body = response.get_json()
    assert "subcategoria" in body["data"]


def test_publicar_anuncio_precio_invalido_retorna_422(client, app):
    with app.app_context():
        usuario = crear_usuario()
        token = token_para_usuario(usuario)

    response = client.post(
        PUBLICAR_URL,
        json=datos_anuncio(precio="0.00"),
        headers=headers_auth(token),
    )

    assert response.status_code == 422
    body = response.get_json()
    assert "precio" in body["data"]


def test_publicar_anuncio_precio_mas_de_dos_decimales_retorna_422(client, app):
    with app.app_context():
        usuario = crear_usuario()
        token = token_para_usuario(usuario)

    response = client.post(
        PUBLICAR_URL,
        json=datos_anuncio(precio="10.999"),
        headers=headers_auth(token),
    )

    assert response.status_code == 422
    body = response.get_json()
    assert "precio" in body["data"]


def test_publicar_anuncio_titulo_largo_retorna_422(client, app):
    with app.app_context():
        usuario = crear_usuario()
        token = token_para_usuario(usuario)

    response = client.post(
        PUBLICAR_URL,
        json=datos_anuncio(titulo="A" * 101),
        headers=headers_auth(token),
    )

    assert response.status_code == 422
    body = response.get_json()
    assert "titulo" in body["data"]


def test_publicar_anuncio_campo_obligatorio_faltante_retorna_400(client, app):
    with app.app_context():
        usuario = crear_usuario()
        token = token_para_usuario(usuario)

    data = datos_anuncio()
    data.pop("subcategoria")
    response = client.post(PUBLICAR_URL, json=data, headers=headers_auth(token))

    assert response.status_code == 400
    body = response.get_json()
    assert "subcategoria" in body["data"]


def test_publicar_anuncio_user_estandar_limite_25_retorna_403(client, app):
    with app.app_context():
        usuario = crear_usuario()
        for i in range(25):
            db.session.add(Anuncio(
                usuario_id=usuario.id,
                titulo=f"Anuncio {i}",
                descripcion="Descripcion",
                categoria="COMPONENTES",
                subcategoria="PROCESADOR",
                condicion="USADO",
                precio="100.00",
                estado="ACTIVO",
            ))
        db.session.commit()
        token = token_para_usuario(usuario)

    response = client.post(
        PUBLICAR_URL,
        json=datos_anuncio(),
        headers=headers_auth(token),
    )

    assert response.status_code == 403
    body = response.get_json()
    assert body["error"] == "FORBIDDEN"
    assert "25 anuncios" in body["message"]


def test_publicar_anuncio_tienda_verificada_sin_limite_25(client, app):
    with app.app_context():
        usuario = crear_usuario(
            correo="tiendaactiva@gmail.com",
            rol="TIENDA_VERIFICADA",
            estado="ACTIVO",
        )
        for i in range(25):
            db.session.add(Anuncio(
                usuario_id=usuario.id,
                titulo=f"Anuncio tienda {i}",
                descripcion="Descripcion",
                categoria="COMPONENTES",
                subcategoria="PROCESADOR",
                condicion="USADO",
                precio="100.00",
                estado="ACTIVO",
            ))
        db.session.commit()
        token = token_para_usuario(usuario)

    response = client.post(
        PUBLICAR_URL,
        json=datos_anuncio(),
        headers=headers_auth(token),
    )

    assert response.status_code == 201
