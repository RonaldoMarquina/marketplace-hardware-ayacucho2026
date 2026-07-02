from datetime import UTC, datetime, timedelta

import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.anuncio import Anuncio
from app.models.calificacion import Calificacion
from app.models.media_anuncio import MediaAnuncio
from app.models.transaccion import Transaccion
from app.models.usuario import Usuario


PASSWORD = "123456#P"
URL = "/api/v1/usuarios/me/transacciones"


def crear_usuario(correo, rol="USER_ESTANDAR", estado="ACTIVO"):
    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")
    usuario = Usuario(
        nombre=f"Usuario {correo}",
        correo=correo,
        password_hash=password_hash,
        telefono=f"9{abs(hash(correo)) % 100000000:08d}",
        rol=rol,
        estado=estado,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def crear_anuncio(usuario, titulo, precio="100.00", created_at=None):
    anuncio = Anuncio(
        usuario_id=usuario.id,
        titulo=titulo,
        descripcion=f"Descripcion {titulo}",
        categoria="COMPONENTES",
        subcategoria="PROCESADOR",
        condicion="USADO",
        precio=precio,
        especificaciones={"socket": "AM4"},
        estado="VENDIDO",
        reactivaciones_count=0,
    )
    if created_at is not None:
        anuncio.created_at = created_at
        anuncio.updated_at = created_at
    db.session.add(anuncio)
    db.session.commit()
    return anuncio


def crear_imagen_principal(anuncio, nombre="principal.jpg"):
    media = MediaAnuncio(
        anuncio_id=anuncio.id,
        tipo_media="imagen",
        ruta_relativa=f"uploads/anuncios/{anuncio.id}/{nombre}",
        es_principal=True,
        orden=0,
    )
    db.session.add(media)
    db.session.commit()
    return media


def crear_transaccion(vendedor, comprador, anuncio, created_at, pend_vendedor=True, pend_comprador=True):
    anuncio.comprador_id = comprador.id
    anuncio.vendido_at = created_at
    transaccion = Transaccion(
        anuncio_id=anuncio.id,
        vendedor_id=vendedor.id,
        comprador_id=comprador.id,
        calificacion_vendedor_pending=pend_vendedor,
        calificacion_comprador_pending=pend_comprador,
        created_at=created_at,
    )
    db.session.add(transaccion)
    db.session.commit()
    return transaccion


def crear_calificacion(transaccion, calificador, calificado, tipo, puntaje, comentario, created_at):
    calificacion = Calificacion(
        transaccion_id=transaccion.id,
        calificador_id=calificador.id,
        calificado_id=calificado.id,
        tipo=tipo,
        puntaje=puntaje,
        comentario=comentario,
        created_at=created_at,
    )
    db.session.add(calificacion)
    db.session.commit()
    return calificacion


def token_para(usuario):
    return create_access_token(
        identity=str(usuario.id),
        additional_claims={"correo": usuario.correo, "rol": usuario.rol},
    )


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_historial_transacciones_ambas_mezcla_ventas_y_compras_ordenadas(client, app):
    with app.app_context():
        yo = crear_usuario("yo@gmail.com")
        comprador = crear_usuario("comprador@gmail.com")
        vendedor = crear_usuario("vendedor@gmail.com", rol="TIENDA_VERIFICADA")
        comprador_nombre = comprador.nombre

        ahora = datetime.now(UTC).replace(tzinfo=None)
        anuncio_venta = crear_anuncio(yo, "Mi venta", precio="450.00", created_at=ahora - timedelta(hours=3))
        anuncio_compra = crear_anuncio(vendedor, "Mi compra", precio="2800.00", created_at=ahora - timedelta(hours=5))
        crear_imagen_principal(anuncio_venta, "venta.jpg")
        crear_imagen_principal(anuncio_compra, "compra.jpg")

        transaccion_venta = crear_transaccion(
            yo, comprador, anuncio_venta, created_at=ahora - timedelta(hours=2), pend_comprador=True
        )
        transaccion_compra = crear_transaccion(
            vendedor, yo, anuncio_compra, created_at=ahora - timedelta(hours=1), pend_vendedor=False
        )
        crear_calificacion(
            transaccion_compra,
            yo,
            vendedor,
            "COMPRADOR_A_VENDEDOR",
            5,
            "Excelente vendedor.",
            created_at=ahora - timedelta(minutes=30),
        )
        token = token_para(yo)

    response = client.get(URL, headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert [item["tipo"] for item in body["data"]] == ["compra", "venta"]
    assert body["data"][0]["anuncio"]["titulo"] == "Mi compra"
    assert body["data"][0]["contraparte"]["es_tienda_verificada"] is True
    assert body["data"][0]["calificacion_pendiente"] is False
    assert body["data"][0]["calificacion_emitida"]["puntaje"] == 5
    assert body["data"][1]["anuncio"]["titulo"] == "Mi venta"
    assert body["data"][1]["contraparte"]["nombre"] == comprador_nombre
    assert body["data"][1]["calificacion_pendiente"] is True
    assert body["data"][1]["calificacion_emitida"] is None
    assert body["resumen"] == {
        "total_ventas": 1,
        "total_compras": 1,
        "calificaciones_pendientes": 1,
    }


def test_historial_transacciones_filtra_ventas_y_resumen_permanece_global(client, app):
    with app.app_context():
        yo = crear_usuario("yo2@gmail.com")
        comprador = crear_usuario("comprador2@gmail.com")
        vendedor = crear_usuario("vendedor2@gmail.com")
        ahora = datetime.now(UTC).replace(tzinfo=None)

        anuncio_venta = crear_anuncio(yo, "Venta", created_at=ahora - timedelta(days=2))
        anuncio_compra = crear_anuncio(vendedor, "Compra", created_at=ahora - timedelta(days=3))
        transaccion_venta = crear_transaccion(yo, comprador, anuncio_venta, created_at=ahora - timedelta(days=1))
        transaccion_compra = crear_transaccion(vendedor, yo, anuncio_compra, created_at=ahora - timedelta(hours=12))
        crear_calificacion(
            transaccion_venta,
            yo,
            comprador,
            "VENDEDOR_A_COMPRADOR",
            4,
            "Comprador serio.",
            created_at=ahora - timedelta(hours=10),
        )
        transaccion_venta.calificacion_comprador_pending = False
        db.session.commit()
        token = token_para(yo)

    response = client.get(f"{URL}?tipo=ventas", headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert len(body["data"]) == 1
    assert body["data"][0]["tipo"] == "venta"
    assert body["resumen"] == {
        "total_ventas": 1,
        "total_compras": 1,
        "calificaciones_pendientes": 1,
    }


def test_historial_transacciones_filtra_compras_y_devuelve_calificacion_emitida(client, app):
    with app.app_context():
        yo = crear_usuario("yo3@gmail.com")
        vendedor = crear_usuario("vendedor3@gmail.com")
        anuncio = crear_anuncio(vendedor, "Compra filtrada", precio="999.99")
        ahora = datetime.now(UTC).replace(tzinfo=None)
        transaccion = crear_transaccion(vendedor, yo, anuncio, created_at=ahora, pend_vendedor=False)
        crear_calificacion(
            transaccion,
            yo,
            vendedor,
            "COMPRADOR_A_VENDEDOR",
            5,
            "Todo bien.",
            created_at=ahora + timedelta(minutes=5),
        )
        token = token_para(yo)

    response = client.get(f"{URL}?tipo=compras", headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert len(body["data"]) == 1
    assert body["data"][0]["tipo"] == "compra"
    assert body["data"][0]["monto"] == 999.99
    assert body["data"][0]["calificacion_emitida"]["comentario"] == "Todo bien."


def test_historial_transacciones_paginacion_limit_20(client, app):
    with app.app_context():
        yo = crear_usuario("yo4@gmail.com")
        comprador = crear_usuario("comprador4@gmail.com")
        ahora = datetime.now(UTC).replace(tzinfo=None)
        for i in range(12):
            anuncio = crear_anuncio(yo, f"Venta {i}", created_at=ahora - timedelta(minutes=i))
            crear_transaccion(yo, comprador, anuncio, created_at=ahora - timedelta(minutes=i))
        token = token_para(yo)

    response = client.get(f"{URL}?tipo=ventas&page=2&limit=10", headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert len(body["data"]) == 2
    assert body["paginacion"] == {
        "total": 12,
        "pagina_actual": 2,
        "total_paginas": 2,
        "limit": 10,
        "tiene_siguiente": False,
        "tiene_anterior": True,
    }


def test_historial_transacciones_tipo_invalido_retorna_422(client, app):
    with app.app_context():
        yo = crear_usuario("yo5@gmail.com")
        token = token_para(yo)

    response = client.get(f"{URL}?tipo=otro", headers=headers(token))

    assert response.status_code == 422
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_historial_transacciones_cuenta_no_activa_retorna_403(client, app):
    with app.app_context():
        yo = crear_usuario("yo6@gmail.com", estado="BLOQUEADO")
        token = token_para(yo)

    response = client.get(URL, headers=headers(token))

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_historial_transacciones_sin_jwt_retorna_401(client):
    response = client.get(URL)

    assert response.status_code == 401


def test_historial_transacciones_limit_invalido_retorna_400(client, app):
    with app.app_context():
        yo = crear_usuario("yo7@gmail.com")
        token = token_para(yo)

    response = client.get(f"{URL}?limit=21", headers=headers(token))

    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"
