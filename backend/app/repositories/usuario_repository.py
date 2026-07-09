from app import db
from app.models.admin_log import AdminLog
from app.models.anuncio import Anuncio
from app.models.media_anuncio import MediaAnuncio
from app.models.tienda import Tienda
from app.models.transaccion import Transaccion
from app.models.usuario import Usuario


class UsuarioRepository:
    @staticmethod
    def buscar_usuario_y_tienda(usuario_id):
        return db.session.query(
            Usuario,
            Tienda,
        ).outerjoin(
            Tienda,
            Tienda.usuario_id == Usuario.id,
        ).filter(
            Usuario.id == usuario_id,
        ).first()

    @staticmethod
    def buscar_usuario_por_telefono(telefono):
        return Usuario.query.filter_by(telefono=telefono).first()

    @staticmethod
    def buscar_tienda_por_nombre_comercial(nombre_comercial):
        return Tienda.query.filter_by(nombre_comercial=nombre_comercial).first()

    @staticmethod
    def listar_usuarios_admin(estado=None, rol=None, q=None, offset=0, limit=20):
        query = db.session.query(
            Usuario,
            Tienda.nombre_comercial.label("nombre_comercial"),
            Tienda.ruc.label("ruc"),
        ).outerjoin(
            Tienda,
            Tienda.usuario_id == Usuario.id,
        )

        if estado:
            query = query.filter(Usuario.estado == estado)
        if rol:
            query = query.filter(Usuario.rol == rol)
        if q:
            like_term = f"%{q}%"
            query = query.filter(
                db.or_(
                    Usuario.nombre.ilike(like_term),
                    Usuario.correo.ilike(like_term),
                )
            )

        query = query.order_by(Usuario.created_at.desc(), Usuario.id.desc())
        total = db.session.query(db.func.count()).select_from(query.order_by(None).subquery()).scalar()
        items = query.offset(offset).limit(limit).all()
        return items, total

    @staticmethod
    def buscar_usuario_admin_detalle(usuario_id):
        return db.session.query(
            Usuario,
            Tienda,
        ).outerjoin(
            Tienda,
            Tienda.usuario_id == Usuario.id,
        ).filter(
            Usuario.id == usuario_id,
        ).first()

    @staticmethod
    def listar_anuncios_activos_publicos(usuario_id, limit=10):
        return UsuarioRepository.listar_anuncios_por_estado_publicos(usuario_id, "ACTIVO", limit=limit)

    @staticmethod
    def listar_anuncios_por_estado_publicos(usuario_id, estado, limit=10):
        return db.session.query(
            Anuncio.id,
            Anuncio.titulo,
            Anuncio.precio,
            Anuncio.categoria,
            Anuncio.subcategoria,
            Anuncio.condicion,
            Anuncio.created_at,
            Anuncio.updated_at,
            MediaAnuncio.ruta_relativa.label("imagen_principal"),
        ).outerjoin(
            MediaAnuncio,
            db.and_(
                MediaAnuncio.anuncio_id == Anuncio.id,
                MediaAnuncio.tipo_media == "imagen",
                MediaAnuncio.es_principal.is_(True),
            ),
        ).filter(
            Anuncio.usuario_id == usuario_id,
            Anuncio.estado == estado,
        ).order_by(
            Anuncio.created_at.desc(),
            Anuncio.id.desc(),
        ).limit(limit).all()

    @staticmethod
    def contar_anuncios_activos(usuario_id):
        return Anuncio.query.filter_by(usuario_id=usuario_id, estado="ACTIVO").count()

    @staticmethod
    def contar_ventas(usuario_id):
        return Transaccion.query.filter_by(vendedor_id=usuario_id).count()

    @staticmethod
    def contar_compras(usuario_id):
        return Transaccion.query.filter_by(comprador_id=usuario_id).count()

    @staticmethod
    def contar_anuncios_por_estado(usuario_id):
        rows = db.session.query(
            Anuncio.estado,
            db.func.count(Anuncio.id),
        ).filter(
            Anuncio.usuario_id == usuario_id,
            Anuncio.estado.in_(("ACTIVO", "INACTIVO", "VENDIDO")),
        ).group_by(Anuncio.estado).all()
        return {estado: total for estado, total in rows}

    @staticmethod
    def contar_calificaciones_pendientes(usuario_id):
        return Transaccion.query.filter(
            db.or_(
                db.and_(
                    Transaccion.vendedor_id == usuario_id,
                    Transaccion.calificacion_comprador_pending.is_(True),
                ),
                db.and_(
                    Transaccion.comprador_id == usuario_id,
                    Transaccion.calificacion_vendedor_pending.is_(True),
                ),
            )
        ).count()

    @staticmethod
    def listar_historial_admin_usuario(usuario_id, limit=5):
        return AdminLog.query.filter(
            AdminLog.usuario_id == usuario_id,
        ).order_by(
            AdminLog.created_at.desc(),
            AdminLog.id.desc(),
        ).limit(limit).all()

    @staticmethod
    def desactivar_anuncios_activos_usuario(usuario_id):
        return Anuncio.query.filter_by(
            usuario_id=usuario_id,
            estado="ACTIVO",
        ).update(
            {"estado": "INACTIVO"},
            synchronize_session=False,
        )

    @staticmethod
    def agregar_admin_log(log_entry):
        db.session.add(log_entry)

    @staticmethod
    def flush():
        db.session.flush()

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
