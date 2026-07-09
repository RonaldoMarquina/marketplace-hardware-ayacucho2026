import pytest

pytestmark = pytest.mark.integration

from datetime import UTC, datetime, timedelta

import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.anuncio import Anuncio
from app.models.tienda import Tienda
from app.models.transaccion import Transaccion
from app.models.usuario import Usuario


PASSWORD = "123456#P"
URL = "/api/v1/usuarios/me/panel"


def crear_usuario(correo, rol="USER_ESTANDAR", estado="ACTIVO", telefono=None):
    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")
    usuario = Usuario(
        nombre=f"Usuario {correo}",
        correo=correo,
        password_hash=password_hash,
        telefono=telefono if telefono is not None else f"9{abs(hash(correo)) % 100000000:08d}",
        rol=rol,
        estado=estado,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def crear_tienda(usuario, estado="ACTIVO"):
    tienda = Tienda(
        usuario_id=usuario.id,
        nombre_comercial=f"Tienda {usuario.id}",
        ruc=f"{10000000000 + usuario.id}",
        direccion=f"Jr. Comercio {usuario.id}",
        documento_identidad=f"uploads/tiendas/{usuario.id}/dni.pdf",
        estado=estado,
    )
    db.session.add(tienda)
    db.session.commit()
    return tienda


def crear_anuncio(usuario, titulo, estado="ACTIVO"):
    anuncio = Anuncio(
        usuario_id=usuario.id,
        titulo=titulo,
        descripcion=f"Descripcion {titulo}",
        categoria="COMPONENTES",
        subcategoria="PROCESADOR",
        condicion="USADO",
        precio="100.00",
        especificaciones={"socket": "AM4"},
        estado=estado,
        reactivaciones_count=0,
    )
    db.session.add(anuncio)
    db.session.commit()
    return anuncio


def crear_transaccion(vendedor, comprador, anuncio, created_at=None, pend_vendedor=True, pend_comprador=True):
    fecha = created_at or datetime.now(UTC).replace(tzinfo=None)
    anuncio.estado = "VENDIDO"
    anuncio.comprador_id = comprador.id
    anuncio.vendido_at = fecha
    transaccion = Transaccion(
        anuncio_id=anuncio.id,
        vendedor_id=vendedor.id,
        comprador_id=comprador.id,
        calificacion_vendedor_pending=pend_vendedor,
        calificacion_comprador_pending=pend_comprador,
        created_at=fecha,
    )
    db.session.add(transaccion)
    db.session.commit()
    return transaccion


def token_para(usuario):
    return create_access_token(
        identity=str(usuario.id),
        additional_claims={"correo": usuario.correo, "rol": usuario.rol},
    )


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_panel_usuario_estandar_retorna_resumen_completo(client, app):
    with app.app_context():
        yo = crear_usuario("panel@gmail.com", telefono="987654321")
        comprador = crear_usuario("comprador_panel@gmail.com")
        vendedor = crear_usuario("vendedor_panel@gmail.com")
        yo_id = yo.id
        yo_nombre = yo.nombre
        yo_correo = yo.correo
        yo.calificacion_promedio_vendedor = 4.8
        yo.total_calificaciones_vendedor = 23
        yo.calificacion_promedio_comprador = 4.6
        yo.total_calificaciones_comprador = 11
        db.session.commit()

        crear_anuncio(yo, "Activo 1", estado="ACTIVO")
        crear_anuncio(yo, "Activo 2", estado="ACTIVO")
        crear_anuncio(yo, "Activo 3", estado="ACTIVO")
        crear_anuncio(yo, "Inactivo 1", estado="INACTIVO")
        crear_anuncio(yo, "Inactivo 2", estado="INACTIVO")

        for i in range(18):
            anuncio_vendido = crear_anuncio(yo, f"Vendido {i}", estado="ACTIVO")
            crear_transaccion(yo, comprador, anuncio_vendido, created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=i), pend_comprador=(i < 2))

        for i in range(11):
            anuncio_compra = crear_anuncio(vendedor, f"Compra {i}", estado="ACTIVO")
            crear_transaccion(vendedor, yo, anuncio_compra, created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=30 + i), pend_vendedor=False)

        token = token_para(yo)

    response = client.get(URL, headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["perfil"] == {
        "id": yo_id,
        "nombre": yo_nombre,
        "correo": yo_correo,
        "telefono": "987654321",
        "es_tienda_verificada": False,
        "estado": "ACTIVO",
        "miembro_desde": body["data"]["perfil"]["miembro_desde"],
    }
    assert body["data"]["anuncios"] == {
        "activos": {
            "total": 3,
            "limite_maximo": 25,
            "disponibles": 22,
        },
        "inactivos": {
            "total": 2,
            "items": [
                {
                    "id": body["data"]["anuncios"]["inactivos"]["items"][0]["id"],
                    "titulo": "Inactivo 2",
                    "precio": 100.0,
                    "categoria": "COMPONENTES",
                    "subcategoria": "PROCESADOR",
                    "condicion": "USADO",
                    "imagen_principal": None,
                    "created_at": body["data"]["anuncios"]["inactivos"]["items"][0]["created_at"],
                    "updated_at": body["data"]["anuncios"]["inactivos"]["items"][0]["updated_at"],
                },
                {
                    "id": body["data"]["anuncios"]["inactivos"]["items"][1]["id"],
                    "titulo": "Inactivo 1",
                    "precio": 100.0,
                    "categoria": "COMPONENTES",
                    "subcategoria": "PROCESADOR",
                    "condicion": "USADO",
                    "imagen_principal": None,
                    "created_at": body["data"]["anuncios"]["inactivos"]["items"][1]["created_at"],
                    "updated_at": body["data"]["anuncios"]["inactivos"]["items"][1]["updated_at"],
                },
            ],
        },
        "vendidos": {
            "total": 18,
        },
    }
    assert body["data"]["reputacion_vendedor"] == {
        "calificacion_promedio": 4.8,
        "total_calificaciones": 23,
        "total_ventas": 18,
    }
    assert body["data"]["reputacion_comprador"] == {
        "calificacion_promedio": 4.6,
        "total_calificaciones": 11,
        "total_compras": 11,
    }
    assert body["data"]["calificaciones_pendientes"] == 2


def test_panel_tienda_verificada_retorna_limites_null_y_tienda_privada(client, app):
    with app.app_context():
        yo = crear_usuario("tienda_panel@gmail.com", rol="TIENDA_VERIFICADA", telefono="999888777")
        tienda = crear_tienda(yo)
        yo.calificacion_promedio_vendedor = 4.9
        yo.total_calificaciones_vendedor = 87
        yo.calificacion_promedio_comprador = 5.0
        yo.total_calificaciones_comprador = 3
        db.session.commit()

        for i in range(12):
            crear_anuncio(yo, f"Activo tienda {i}", estado="ACTIVO")
        for i in range(5):
            crear_anuncio(yo, f"Inactivo tienda {i}", estado="INACTIVO")

        comprador = crear_usuario("comprador_tienda_panel@gmail.com")
        for i in range(84):
            anuncio_vendido = crear_anuncio(yo, f"Vendido tienda {i}", estado="ACTIVO")
            crear_transaccion(yo, comprador, anuncio_vendido, pend_comprador=False)
        vendedor = crear_usuario("otro_vendedor_panel@gmail.com")
        for i in range(3):
            anuncio_compra = crear_anuncio(vendedor, f"Compra tienda {i}", estado="ACTIVO")
            crear_transaccion(vendedor, yo, anuncio_compra, pend_vendedor=False)

        token = token_para(yo)
        nombre_comercial = tienda.nombre_comercial
        ruc = tienda.ruc
        direccion = tienda.direccion

    response = client.get(URL, headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["perfil"]["es_tienda_verificada"] is True
    assert body["data"]["perfil"]["tienda"] == {
        "nombre_comercial": nombre_comercial,
        "ruc": ruc,
        "direccion": direccion,
    }
    assert body["data"]["anuncios"]["activos"] == {
        "total": 12,
        "limite_maximo": None,
        "disponibles": None,
    }
    assert body["data"]["anuncios"]["inactivos"]["total"] == 5
    assert len(body["data"]["anuncios"]["inactivos"]["items"]) == 5
    assert body["data"]["anuncios"]["vendidos"]["total"] == 84
    assert body["data"]["reputacion_vendedor"]["total_ventas"] == 84
    assert body["data"]["reputacion_comprador"]["total_compras"] == 3
    assert body["data"]["calificaciones_pendientes"] == 0


def test_panel_usuario_cuenta_no_activa_retorna_403(client, app):
    with app.app_context():
        yo = crear_usuario("panel_blocked@gmail.com", estado="BLOQUEADO")
        token = token_para(yo)

    response = client.get(URL, headers=headers(token))

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_panel_usuario_sin_jwt_retorna_401(client):
    response = client.get(URL)

    assert response.status_code == 401

