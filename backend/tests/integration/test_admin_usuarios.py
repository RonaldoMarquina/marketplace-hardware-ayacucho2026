import pytest

pytestmark = pytest.mark.integration

from datetime import UTC, datetime, timedelta

import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.admin_log import AdminLog
from app.models.anuncio import Anuncio
from app.models.tienda import Tienda
from app.models.transaccion import Transaccion
from app.models.usuario import Usuario


PASSWORD = "123456#P"
ADMIN_URL = "/api/v1/admin/usuarios"
LOGIN_URL = "/api/v1/auth/login"


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


def crear_tienda(usuario, estado="EN_REVISION"):
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


def crear_transaccion(vendedor, comprador, anuncio, created_at=None):
    fecha = created_at or datetime.now(UTC).replace(tzinfo=None)
    anuncio.estado = "VENDIDO"
    anuncio.comprador_id = comprador.id
    anuncio.vendido_at = fecha
    transaccion = Transaccion(
        anuncio_id=anuncio.id,
        vendedor_id=vendedor.id,
        comprador_id=comprador.id,
        calificacion_vendedor_pending=False,
        calificacion_comprador_pending=False,
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


def test_admin_lista_usuarios_con_filtros(client, app):
    with app.app_context():
        admin = crear_usuario("admin@gmail.com", rol="ADMIN")
        tienda_user = crear_usuario("tienda@gmail.com", rol="TIENDA_VERIFICADA", estado="EN_REVISION", telefono="987654322")
        tienda = crear_tienda(tienda_user)
        crear_usuario("juan@gmail.com", rol="USER_ESTANDAR", estado="ACTIVO", telefono="987654321")
        token = token_para(admin)
        nombre_comercial = tienda.nombre_comercial
        ruc = tienda.ruc

    response = client.get(
        f"{ADMIN_URL}?estado=EN_REVISION&rol=TIENDA_VERIFICADA&q=tienda&page=1&limit=20",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert len(body["data"]) == 1
    assert body["data"][0]["correo"] == "tienda@gmail.com"
    assert body["data"][0]["nombre_comercial"] == nombre_comercial
    assert body["data"][0]["ruc"] == ruc


def test_admin_detalle_usuario_retorna_tienda_reputacion_e_historial(client, app):
    with app.app_context():
        admin = crear_usuario("admin2@gmail.com", rol="ADMIN")
        usuario = crear_usuario("detalle@gmail.com", rol="TIENDA_VERIFICADA", estado="EN_REVISION")
        tienda = crear_tienda(usuario)
        comprador = crear_usuario("comprador_detalle@gmail.com")
        usuario.calificacion_promedio_vendedor = 4.9
        usuario.total_calificaciones_vendedor = 10
        usuario.calificacion_promedio_comprador = 4.5
        usuario.total_calificaciones_comprador = 2
        db.session.commit()
        for i in range(3):
            anuncio = crear_anuncio(usuario, f"Venta {i}", estado="ACTIVO")
            crear_transaccion(usuario, comprador, anuncio, created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=i))
        for i in range(2):
            anuncio = crear_anuncio(comprador, f"Compra {i}", estado="ACTIVO")
            crear_transaccion(comprador, usuario, anuncio, created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=10 + i))
        for i in range(2):
            db.session.add(AdminLog(
                admin_id=admin.id,
                usuario_id=usuario.id,
                anuncio_id=None,
                accion="USUARIO_BLOQUEADO" if i == 0 else "USUARIO_DESBLOQUEADO",
                motivo="Motivo prueba",
                created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=i),
            ))
        db.session.commit()
        token = token_para(admin)
        usuario_id = usuario.id
        documento = tienda.documento_identidad

    response = client.get(f"{ADMIN_URL}/{usuario_id}", headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["correo"] == "detalle@gmail.com"
    assert body["data"]["tienda"]["documento_identidad"] == documento
    assert body["data"]["reputacion_vendedor"]["total_ventas"] == 3
    assert body["data"]["reputacion_comprador"]["total_compras"] == 2
    assert len(body["data"]["historial_admin"]) == 2


def test_admin_activar_usuario_en_revision_exitoso(client, app):
    with app.app_context():
        admin = crear_usuario("admin3@gmail.com", rol="ADMIN")
        usuario = crear_usuario("activar@gmail.com", rol="TIENDA_VERIFICADA", estado="EN_REVISION")
        tienda = crear_tienda(usuario, estado="EN_REVISION")
        token = token_para(admin)
        usuario_id = usuario.id
        nombre_comercial = tienda.nombre_comercial

    response = client.patch(f"{ADMIN_URL}/{usuario_id}/activar", headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["estado"] == "ACTIVO"
    assert body["data"]["nombre_comercial"] == nombre_comercial

    with app.app_context():
        usuario_db = db.session.get(Usuario, usuario_id)
        tienda_db = Tienda.query.filter_by(usuario_id=usuario_id).first()
        log_entry = AdminLog.query.filter_by(usuario_id=usuario_id, accion="USUARIO_ACTIVADO").first()
        assert usuario_db.estado == "ACTIVO"
        assert tienda_db.estado == "ACTIVO"
        assert log_entry is not None


def test_admin_rechazar_tienda_en_revision_exitoso(client, app):
    with app.app_context():
        admin = crear_usuario("admin4@gmail.com", rol="ADMIN")
        usuario = crear_usuario("rechazar@gmail.com", rol="TIENDA_VERIFICADA", estado="EN_REVISION")
        crear_tienda(usuario, estado="EN_REVISION")
        token = token_para(admin)
        usuario_id = usuario.id

    response = client.patch(
        f"{ADMIN_URL}/{usuario_id}/rechazar",
        json={"motivo": "Documento ilegible."},
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["estado"] == "RECHAZADO"
    assert body["data"]["motivo"] == "Documento ilegible."

    with app.app_context():
        usuario_db = db.session.get(Usuario, usuario_id)
        tienda_db = Tienda.query.filter_by(usuario_id=usuario_id).first()
        assert usuario_db.estado == "RECHAZADO"
        assert tienda_db.estado == "RECHAZADO"


def test_admin_bloquear_usuario_desactiva_anuncios_activos(client, app):
    with app.app_context():
        admin = crear_usuario("admin5@gmail.com", rol="ADMIN")
        usuario = crear_usuario("bloquear@gmail.com", estado="ACTIVO")
        crear_anuncio(usuario, "Activo 1", estado="ACTIVO")
        crear_anuncio(usuario, "Activo 2", estado="ACTIVO")
        crear_anuncio(usuario, "Inactivo", estado="INACTIVO")
        token = token_para(admin)
        usuario_id = usuario.id

    response = client.patch(
        f"{ADMIN_URL}/{usuario_id}/bloquear",
        json={"motivo": "Fraude confirmado."},
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["estado"] == "BLOQUEADO"
    assert body["data"]["anuncios_desactivados"] == 2

    with app.app_context():
        usuario_db = db.session.get(Usuario, usuario_id)
        activos = Anuncio.query.filter_by(usuario_id=usuario_id, estado="ACTIVO").count()
        inactivos = Anuncio.query.filter_by(usuario_id=usuario_id, estado="INACTIVO").count()
        assert usuario_db.estado == "BLOQUEADO"
        assert activos == 0
        assert inactivos == 3


def test_admin_desbloquear_usuario_no_reactiva_anuncios(client, app):
    with app.app_context():
        admin = crear_usuario("admin6@gmail.com", rol="ADMIN")
        usuario = crear_usuario("desbloquear@gmail.com", estado="BLOQUEADO")
        crear_anuncio(usuario, "Inactivo", estado="INACTIVO")
        token = token_para(admin)
        usuario_id = usuario.id

    response = client.patch(
        f"{ADMIN_URL}/{usuario_id}/desbloquear",
        json={"motivo": "Reportes no confirmados."},
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["estado"] == "ACTIVO"

    with app.app_context():
        usuario_db = db.session.get(Usuario, usuario_id)
        inactivos = Anuncio.query.filter_by(usuario_id=usuario_id, estado="INACTIVO").count()
        assert usuario_db.estado == "ACTIVO"
        assert inactivos == 1


def test_admin_bloquear_admin_retorna_422(client, app):
    with app.app_context():
        admin = crear_usuario("admin7@gmail.com", rol="ADMIN")
        otro_admin = crear_usuario("admin8@gmail.com", rol="ADMIN")
        token = token_para(admin)
        otro_admin_id = otro_admin.id

    response = client.patch(
        f"{ADMIN_URL}/{otro_admin_id}/bloquear",
        json={"motivo": "No permitido."},
        headers=headers(token),
    )

    assert response.status_code == 422
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_admin_no_admin_retorna_403(client, app):
    with app.app_context():
        usuario = crear_usuario("user@gmail.com")
        token = token_para(usuario)

    response = client.get(ADMIN_URL, headers=headers(token))

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_login_cuenta_rechazada_retorna_403(client, app):
    with app.app_context():
        crear_usuario("rechazada_login@gmail.com", estado="RECHAZADO", rol="TIENDA_VERIFICADA")

    response = client.post(
        LOGIN_URL,
        json={"correo": "rechazada_login@gmail.com", "password": PASSWORD},
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "ACCOUNT_REJECTED"

