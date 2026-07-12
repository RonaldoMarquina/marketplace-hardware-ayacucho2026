import pytest

pytestmark = pytest.mark.integration

from datetime import UTC, datetime, timedelta
from io import BytesIO

import bcrypt
from flask_jwt_extended import create_access_token

from app import db
from app.models.apelacion_evidencia import ApelacionEvidencia
from app.models.apelacion_moderacion import ApelacionModeracion
from app.models.anuncio import Anuncio
from app.models.moderacion_log import ModeracionLog
from app.models.reporte import Reporte
from app.models.reporte_evidencia import ReporteEvidencia
from app.models.usuario import Usuario


PASSWORD = "123456#P"


def crear_usuario(correo, rol="USER_ESTANDAR", estado="ACTIVO", **overrides):
    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")
    usuario = Usuario(
        nombre=f"Usuario {correo}",
        correo=correo,
        password_hash=password_hash,
        telefono=f"9{abs(hash(correo)) % 100000000:08d}",
        rol=rol,
        estado=estado,
    )
    for campo, valor in overrides.items():
        setattr(usuario, campo, valor)
    db.session.add(usuario)
    db.session.commit()
    return usuario


def crear_anuncio(usuario, **overrides):
    anuncio = Anuncio(
        usuario_id=usuario.id,
        titulo="Ryzen 5 5600X",
        descripcion="Descripcion",
        categoria="COMPONENTES",
        subcategoria="PROCESADOR",
        condicion="USADO",
        precio="350.00",
        estado="ACTIVO",
        reactivaciones_count=0,
    )
    for campo, valor in overrides.items():
        setattr(anuncio, campo, valor)
    db.session.add(anuncio)
    db.session.commit()
    return anuncio


def crear_reporte(comprador, anuncio, motivo="FRAUDE", estado="PENDIENTE", created_at=None, detalle=None):
    reporte = Reporte(
        comprador_id=comprador.id,
        anuncio_id=anuncio.id,
        motivo=motivo,
        detalle=detalle,
        estado=estado,
        created_at=created_at or datetime.now(UTC).replace(tzinfo=None),
    )
    db.session.add(reporte)
    db.session.commit()
    return reporte


def token_para(usuario):
    return create_access_token(
        identity=str(usuario.id),
        additional_claims={"correo": usuario.correo, "rol": usuario.rol},
    )


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_reportar_anuncio_exitoso(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador@gmail.com")
        vendedor = crear_usuario("vendedor@gmail.com")
        anuncio = crear_anuncio(vendedor)
        token = token_para(comprador)
        anuncio_id = anuncio.id

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "fraude", "detalle": "El producto parece falsificado."},
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["anuncio_id"] == anuncio_id
    assert body["data"]["motivo"] == "FRAUDE"
    assert body["data"]["detalle"] == "El producto parece falsificado."
    assert body["data"]["estado"] == "PENDIENTE"


def test_reportar_anuncio_envia_correo_al_vendedor(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador-mail@gmail.com")
        vendedor = crear_usuario("vendedor-mail@gmail.com")
        anuncio = crear_anuncio(vendedor, titulo="Gabinete Corsair 4000D")
        token = token_para(comprador)
        anuncio_id = anuncio.id
        app.extensions["mail_outbox"] = []

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "PRECIO_ENGANOSO", "detalle": "El precio no coincide con la descripcion."},
        headers=headers(token),
    )

    assert response.status_code == 200
    with app.app_context():
        outbox = app.extensions.get("mail_outbox", [])
        assert len(outbox) == 1
        assert outbox[0]["kind"] == "listing_reported"
        assert outbox[0]["to"] == "vendedor-mail@gmail.com"
        assert outbox[0]["reason"] == "PRECIO_ENGANOSO"


def test_reportar_anuncio_duplicado_en_mismo_ciclo_retorna_409(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador2@gmail.com")
        vendedor = crear_usuario("vendedor2@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, estado="REVISADO")
        token = token_para(comprador)
        anuncio_id = anuncio.id

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "FRAUDE"},
        headers=headers(token),
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "CONFLICT"


def test_reportar_anuncio_nuevo_ciclo_tras_desbloqueo_permitido(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador3@gmail.com")
        vendedor = crear_usuario("vendedor3@gmail.com")
        admin = crear_usuario("admin@gmail.com", rol="ADMIN")
        anuncio = crear_anuncio(vendedor)
        token_comprador = token_para(comprador)
        token_admin = token_para(admin)
        anuncio_id = anuncio.id

    primer_reporte = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "FRAUDE"},
        headers=headers(token_comprador),
    )
    assert primer_reporte.status_code == 200

    bloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Fraude confirmado."},
        headers=headers(token_admin),
    )
    assert bloqueo.status_code == 200

    desbloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/desbloquear",
        json={"motivo_admin": "Revisado nuevamente."},
        headers=headers(token_admin),
    )
    assert desbloqueo.status_code == 200

    segundo_reporte = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "OTRO"},
        headers=headers(token_comprador),
    )

    assert segundo_reporte.status_code == 200
    assert segundo_reporte.get_json()["data"]["motivo"] == "OTRO"


def test_reportar_propio_anuncio_retorna_409(client, app):
    with app.app_context():
        usuario = crear_usuario("propio@gmail.com")
        anuncio = crear_anuncio(usuario)
        token = token_para(usuario)
        anuncio_id = anuncio.id

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "FRAUDE"},
        headers=headers(token),
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "CONFLICT"


def test_reportar_anuncio_inactivo_retorna_404(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador4@gmail.com")
        vendedor = crear_usuario("vendedor4@gmail.com")
        anuncio = crear_anuncio(vendedor, estado="INACTIVO")
        token = token_para(comprador)
        anuncio_id = anuncio.id

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "FRAUDE"},
        headers=headers(token),
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "NOT_FOUND"


def test_reportar_anuncio_supera_limite_diario_retorna_429(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador5@gmail.com")
        vendedor = crear_usuario("vendedor5@gmail.com")
        anuncios = [crear_anuncio(vendedor, titulo=f"Anuncio {i}") for i in range(11)]
        now = datetime.now(UTC).replace(tzinfo=None)
        for anuncio in anuncios[:10]:
            crear_reporte(comprador, anuncio, created_at=now - timedelta(minutes=5))
        token = token_para(comprador)
        anuncio_id = anuncios[10].id

    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        json={"motivo": "OTRO"},
        headers=headers(token),
    )

    assert response.status_code == 429
    body = response.get_json()
    assert body["error"] == "RATE_LIMIT_REPORTES"
    assert "disponible_en" in body["data"]


def test_admin_lista_reportados_agrupa_pendientes(client, app):
    with app.app_context():
        admin = crear_usuario("admin2@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor6@gmail.com", rol="TIENDA_VERIFICADA")
        comprador_a = crear_usuario("comprador6a@gmail.com")
        comprador_b = crear_usuario("comprador6b@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador_a, anuncio, motivo="FRAUDE")
        crear_reporte(comprador_b, anuncio, motivo="PRODUCTO_FALSO")
        token = token_para(admin)
        anuncio_id = anuncio.id

    response = client.get(
        "/api/v1/admin/anuncios/reportados?page=1&limit=20",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["total_pendientes"] == 1
    assert body["data"][0]["anuncio_id"] == anuncio_id
    assert body["data"][0]["total_reportes"] == 2
    assert set(body["data"][0]["motivos"]) == {"FRAUDE", "PRODUCTO_FALSO"}
    assert body["data"][0]["es_tienda_verificada"] is True


def test_admin_no_admin_retorna_403_en_lista_reportados(client, app):
    with app.app_context():
        usuario = crear_usuario("noadmin@gmail.com")
        token = token_para(usuario)

    response = client.get(
        "/api/v1/admin/anuncios/reportados",
        headers=headers(token),
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_admin_bloquear_anuncio_actualiza_estado_reportes_y_log(client, app):
    with app.app_context():
        admin = crear_usuario("admin3@gmail.com", rol="ADMIN")
        comprador = crear_usuario("comprador7@gmail.com")
        vendedor = crear_usuario("vendedor7@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, motivo="FRAUDE")
        token = token_para(admin)
        anuncio_id = anuncio.id

    response = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Anuncio fraudulento confirmado."},
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["estado"] == "BLOQUEADO"

    with app.app_context():
        anuncio_db = db.session.get(Anuncio, anuncio_id)
        reportes = Reporte.query.filter_by(anuncio_id=anuncio_id).all()
        log_entry = ModeracionLog.query.filter_by(anuncio_id=anuncio_id, accion="BLOQUEADO").first()
        assert anuncio_db.estado == "BLOQUEADO"
        assert reportes and all(reporte.estado == "REVISADO" for reporte in reportes)
        assert log_entry is not None
        assert log_entry.motivo_admin == "Anuncio fraudulento confirmado."


def test_admin_desbloquear_anuncio_retorna_activo_y_deja_auditoria(client, app):
    with app.app_context():
        admin = crear_usuario("admin4@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor8@gmail.com")
        anuncio = crear_anuncio(vendedor, estado="BLOQUEADO")
        token = token_para(admin)
        anuncio_id = anuncio.id

    response = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/desbloquear",
        json={"motivo_admin": "Revisado, no se encontro infraccion."},
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["estado"] == "ACTIVO"

    with app.app_context():
        anuncio_db = db.session.get(Anuncio, anuncio_id)
        log_entry = ModeracionLog.query.filter_by(anuncio_id=anuncio_id, accion="DESBLOQUEADO").first()
        assert anuncio_db.estado == "ACTIVO"
        assert log_entry is not None


def test_admin_bloquear_requiere_motivo_admin_no_vacio(client, app):
    with app.app_context():
        admin = crear_usuario("admin5@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor9@gmail.com")
        anuncio = crear_anuncio(vendedor)
        token = token_para(admin)
        anuncio_id = anuncio.id

    response = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "   "},
        headers=headers(token),
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_historial_moderacion_admin_devuelve_eventos(client, app):
    with app.app_context():
        admin = crear_usuario("admin6@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor10@gmail.com")
        anuncio = crear_anuncio(vendedor)
        token = token_para(admin)
        anuncio_id = anuncio.id

    bloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Bloqueado por revision."},
        headers=headers(token),
    )
    assert bloqueo.status_code == 200

    response = client.get(
        "/api/v1/admin/moderacion/historial?page=1&limit=20",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"][0]["anuncio_id"] == anuncio_id
    assert body["data"][0]["accion"] == "BLOQUEADO"


def test_reportar_anuncio_con_evidencia_guarda_archivo_y_registro(client, app):
    with app.app_context():
        comprador = crear_usuario("comprador-evidencia@gmail.com")
        vendedor = crear_usuario("vendedor-evidencia@gmail.com")
        anuncio = crear_anuncio(vendedor)
        token = token_para(comprador)
        anuncio_id = anuncio.id

    png_file = (BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0DIHDR"), "evidencia.png")
    response = client.post(
        f"/api/v1/anuncios/{anuncio_id}/reportar",
        data={
            "motivo": "PRODUCTO_FALSO",
            "detalle": "Adjunto imagen como evidencia.",
            "evidencias": [png_file],
        },
        headers=headers(token),
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["motivo"] == "PRODUCTO_FALSO"
    assert len(body["data"]["evidencias"]) == 1

    with app.app_context():
        evidencia = ReporteEvidencia.query.first()
        assert evidencia is not None
        assert evidencia.ruta_relativa.startswith("uploads/reportes/")


def test_admin_detalle_anuncio_reportado_devuelve_reportes_y_evidencias(client, app):
    with app.app_context():
        admin = crear_usuario("admin-detalle@gmail.com", rol="ADMIN")
        comprador = crear_usuario("comprador-detalle@gmail.com")
        vendedor = crear_usuario("vendedor-detalle@gmail.com")
        anuncio = crear_anuncio(vendedor)
        reporte = crear_reporte(comprador, anuncio, motivo="FRAUDE")
        evidencia = ReporteEvidencia(
            reporte_id=reporte.id,
            ruta_relativa="uploads/reportes/1/evidencia.png",
        )
        db.session.add(evidencia)
        db.session.commit()
        token = token_para(admin)
        anuncio_id = anuncio.id

    response = client.get(
        f"/api/v1/admin/anuncios/{anuncio_id}/reportes",
        headers=headers(token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["anuncio_id"] == anuncio_id
    assert len(body["data"]["reportes"]) == 1
    assert body["data"]["reportes"][0]["evidencias"][0]["ruta_relativa"] == "uploads/reportes/1/evidencia.png"


def test_panel_usuario_incluye_caso_bloqueado_para_apelar(client, app):
    with app.app_context():
        admin = crear_usuario("admin-panel-moderacion@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor-panel-moderacion@gmail.com", rol="TIENDA_VERIFICADA")
        comprador = crear_usuario("comprador-panel-moderacion@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, motivo="PRODUCTO_FALSO")
        token_admin = token_para(admin)
        token_vendedor = token_para(vendedor)
        anuncio_id = anuncio.id

    bloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Se detecto inconsistencia en el anuncio."},
        headers=headers(token_admin),
    )
    assert bloqueo.status_code == 200

    response = client.get(
        "/api/v1/usuarios/me/panel",
        headers=headers(token_vendedor),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["moderacion"]["casos"][0]["anuncio_id"] == anuncio_id
    assert body["data"]["moderacion"]["casos"][0]["puede_apelar"] is True


def test_panel_usuario_incluye_anuncio_reportado_en_revision(client, app):
    with app.app_context():
        vendedor = crear_usuario("vendedor-panel-reportado@gmail.com", rol="TIENDA_VERIFICADA")
        comprador = crear_usuario("comprador-panel-reportado@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, motivo="PRECIO_ENGANOSO", detalle="El precio publicado no coincide.")
        token_vendedor = token_para(vendedor)
        anuncio_id = anuncio.id

    response = client.get(
        "/api/v1/usuarios/me/panel",
        headers=headers(token_vendedor),
    )

    assert response.status_code == 200
    body = response.get_json()
    caso = body["data"]["moderacion"]["casos"][0]
    assert caso["anuncio_id"] == anuncio_id
    assert caso["estado_caso"] == "REPORTADO_EN_REVISION"
    assert caso["motivo_reporte"] == "PRECIO_ENGANOSO"
    assert caso["total_reportes_pendientes"] == 1
    assert caso["puede_apelar"] is False


def test_propietario_puede_ver_detalle_de_anuncio_reportado_aun_no_bloqueado(client, app):
    with app.app_context():
        vendedor = crear_usuario("vendedor-detalle-reportado@gmail.com")
        comprador = crear_usuario("comprador-detalle-reportado@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, motivo="PRODUCTO_FALSO", detalle="No coincide con la descripcion.")
        token_vendedor = token_para(vendedor)
        anuncio_id = anuncio.id

    response = client.get(
        f"/api/v1/usuarios/me/anuncios/{anuncio_id}/moderacion",
        headers=headers(token_vendedor),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["anuncio_id"] == anuncio_id
    assert body["data"]["estado_caso"] == "REPORTADO_EN_REVISION"
    assert body["data"]["motivo_bloqueo"] is None
    assert body["data"]["puede_apelar"] is False
    assert len(body["data"]["reportes"]) == 1


def test_vendedor_puede_apelar_anuncio_bloqueado_con_evidencia(client, app):
    with app.app_context():
        admin = crear_usuario("admin-apelacion@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor-apelacion@gmail.com")
        comprador = crear_usuario("comprador-apelacion@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, motivo="FRAUDE")
        token_admin = token_para(admin)
        token_vendedor = token_para(vendedor)
        anuncio_id = anuncio.id

    bloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Se bloquea mientras se revisa."},
        headers=headers(token_admin),
    )
    assert bloqueo.status_code == 200

    png_file = (BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0DIHDR"), "defensa.png")
    response = client.post(
        f"/api/v1/usuarios/me/anuncios/{anuncio_id}/apelar",
        data={
            "mensaje": "El producto es legitimo y adjunto evidencia de compra original.",
            "evidencias": [png_file],
        },
        headers=headers(token_vendedor),
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    with app.app_context():
        apelacion = ApelacionModeracion.query.filter_by(anuncio_id=anuncio_id).first()
        evidencia = ApelacionEvidencia.query.filter_by(apelacion_id=apelacion.id).first()
        assert apelacion is not None
        assert apelacion.estado == "PENDIENTE"
        assert evidencia is not None
        assert evidencia.ruta_relativa.startswith("uploads/apelaciones/")


def test_apelar_mismo_ciclo_dos_veces_retorna_409(client, app):
    with app.app_context():
        admin = crear_usuario("admin-apelacion-duplicada@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor-apelacion-duplicada@gmail.com")
        comprador = crear_usuario("comprador-apelacion-duplicada@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, motivo="FRAUDE")
        token_admin = token_para(admin)
        token_vendedor = token_para(vendedor)
        anuncio_id = anuncio.id

    bloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Bloqueado por investigacion."},
        headers=headers(token_admin),
    )
    assert bloqueo.status_code == 200

    primer_intento = client.post(
        f"/api/v1/usuarios/me/anuncios/{anuncio_id}/apelar",
        json={"mensaje": "Solicito revision porque tengo comprobantes validos."},
        headers=headers(token_vendedor),
    )
    assert primer_intento.status_code == 200

    segundo_intento = client.post(
        f"/api/v1/usuarios/me/anuncios/{anuncio_id}/apelar",
        json={"mensaje": "Insisto con una segunda apelacion en el mismo ciclo."},
        headers=headers(token_vendedor),
    )

    assert segundo_intento.status_code == 409
    assert segundo_intento.get_json()["error"] == "CONFLICT"


def test_admin_lista_apelaciones_y_detalle_incluye_descargo(client, app):
    with app.app_context():
        admin = crear_usuario("admin-lista-apelaciones@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor-lista-apelaciones@gmail.com")
        comprador = crear_usuario("comprador-lista-apelaciones@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, motivo="PRODUCTO_FALSO")
        token_admin = token_para(admin)
        token_vendedor = token_para(vendedor)
        anuncio_id = anuncio.id

    bloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Se requiere descargo del vendedor."},
        headers=headers(token_admin),
    )
    assert bloqueo.status_code == 200

    apelacion = client.post(
        f"/api/v1/usuarios/me/anuncios/{anuncio_id}/apelar",
        json={"mensaje": "Adjuntare boleta y evidencia del origen del producto."},
        headers=headers(token_vendedor),
    )
    assert apelacion.status_code == 200

    listado = client.get("/api/v1/admin/apelaciones?page=1&limit=20", headers=headers(token_admin))
    assert listado.status_code == 200
    assert listado.get_json()["data"][0]["anuncio_id"] == anuncio_id

    detalle = client.get(f"/api/v1/admin/anuncios/{anuncio_id}/reportes", headers=headers(token_admin))
    assert detalle.status_code == 200
    assert len(detalle.get_json()["data"]["apelaciones"]) == 1


def test_admin_aceptar_apelacion_desbloquea_anuncio(client, app):
    with app.app_context():
        admin = crear_usuario("admin-resuelve-apelacion@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor-resuelve-apelacion@gmail.com")
        comprador = crear_usuario("comprador-resuelve-apelacion@gmail.com")
        anuncio = crear_anuncio(vendedor)
        crear_reporte(comprador, anuncio, motivo="FRAUDE")
        token_admin = token_para(admin)
        token_vendedor = token_para(vendedor)
        anuncio_id = anuncio.id

    bloqueo = client.patch(
        f"/api/v1/admin/anuncios/{anuncio_id}/bloquear",
        json={"motivo_admin": "Bloqueado hasta aclaracion."},
        headers=headers(token_admin),
    )
    assert bloqueo.status_code == 200

    apelacion = client.post(
        f"/api/v1/usuarios/me/anuncios/{anuncio_id}/apelar",
        json={"mensaje": "Solicito desbloqueo porque el reporte fue incorrecto."},
        headers=headers(token_vendedor),
    )
    assert apelacion.status_code == 200
    apelacion_id = apelacion.get_json()["data"]["id"]

    resolver = client.patch(
        f"/api/v1/admin/apelaciones/{apelacion_id}/resolver",
        json={"decision": "ACEPTAR", "motivo_admin": "Se valida el descargo y se rehabilita."},
        headers=headers(token_admin),
    )

    assert resolver.status_code == 200
    with app.app_context():
        anuncio_db = db.session.get(Anuncio, anuncio_id)
        apelacion_db = db.session.get(ApelacionModeracion, apelacion_id)
        reportes = Reporte.query.filter_by(anuncio_id=anuncio_id).all()
        assert anuncio_db.estado == "ACTIVO"
        assert apelacion_db.estado == "ACEPTADA"
        assert reportes and all(reporte.estado == "REVISADO" for reporte in reportes)


def test_admin_lista_reportados_prioriza_caso_con_reportante_mas_confiable(client, app):
    with app.app_context():
        admin = crear_usuario("admin-prioridad@gmail.com", rol="ADMIN")
        vendedor_a = crear_usuario("vendedor-prioridad-a@gmail.com")
        vendedor_b = crear_usuario("vendedor-prioridad-b@gmail.com")
        comprador_confiable = crear_usuario(
            "comprador-confiable@gmail.com",
            created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=90),
            total_calificaciones_comprador=4,
            calificacion_promedio_comprador="4.5",
        )
        comprador_nuevo = crear_usuario(
            "comprador-nuevo@gmail.com",
            created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=1),
        )
        anuncio_alta = crear_anuncio(vendedor_a, titulo="Caso Alta Prioridad")
        anuncio_baja = crear_anuncio(vendedor_b, titulo="Caso Baja Prioridad")
        crear_reporte(comprador_confiable, anuncio_alta, motivo="FRAUDE")
        crear_reporte(comprador_nuevo, anuncio_baja, motivo="OTRO")
        token = token_para(admin)

    response = client.get("/api/v1/admin/anuncios/reportados?page=1&limit=20", headers=headers(token))

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"][0]["titulo"] == "Caso Alta Prioridad"
    assert body["data"][0]["prioridad_score"] >= body["data"][1]["prioridad_score"]
    assert body["data"][0]["prioridad_nivel"] in {"ALTA", "MEDIA"}
    assert "confiabilidad_promedio_reportantes" in body["data"][0]


def test_admin_detalle_caso_expone_senales_operativas_de_abuso(client, app):
    with app.app_context():
        admin = crear_usuario("admin-senales@gmail.com", rol="ADMIN")
        vendedor = crear_usuario("vendedor-senales@gmail.com")
        comprador = crear_usuario(
            "comprador-senales@gmail.com",
            created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=1),
        )
        anuncio_objetivo = crear_anuncio(vendedor, titulo="Objetivo Senales")
        anuncios_previos = [
            crear_anuncio(vendedor, titulo=f"Previo {index}")
            for index in range(4)
        ]
        now = datetime.now(UTC).replace(tzinfo=None)
        crear_reporte(comprador, anuncio_objetivo, motivo="FRAUDE", created_at=now - timedelta(hours=1))
        for anuncio in anuncios_previos:
            crear_reporte(comprador, anuncio, motivo="OTRO", created_at=now - timedelta(days=1))
        token_admin = token_para(admin)
        anuncio_id = anuncio_objetivo.id

    response = client.get(
        f"/api/v1/admin/anuncios/{anuncio_id}/reportes",
        headers=headers(token_admin),
    )

    assert response.status_code == 200
    body = response.get_json()
    report = body["data"]["reportes"][0]
    assert report["senal_reportante"]["nivel"] == "BAJA"
    assert "RAFAGA_REPORTES_7D" in report["senal_reportante"]["senales"]
    assert any(
        signal["codigo"] == "CONCENTRACION_CONTRA_VENDEDOR"
        for signal in body["data"]["senales_operativas"]
    )

