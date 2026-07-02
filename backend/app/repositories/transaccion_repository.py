from app import db
from app.models.calificacion import Calificacion
from app.models.media_anuncio import MediaAnuncio
from app.models.transaccion import Transaccion
from app.models.usuario import Usuario
from app.models.anuncio import Anuncio
from sqlalchemy.orm import aliased


class TransaccionRepository:
    @staticmethod
    def buscar_usuario_por_id(usuario_id):
        return db.session.get(Usuario, usuario_id)

    @staticmethod
    def buscar_transaccion_por_id(transaccion_id):
        return db.session.get(Transaccion, transaccion_id)

    @staticmethod
    def agregar_calificacion(calificacion):
        db.session.add(calificacion)

    @staticmethod
    def obtener_resumen_calificaciones(calificado_id, tipo):
        promedio, total = db.session.query(
            db.func.avg(Calificacion.puntaje),
            db.func.count(Calificacion.id),
        ).filter(
            Calificacion.calificado_id == calificado_id,
            Calificacion.tipo == tipo,
        ).one()
        return promedio, total

    @staticmethod
    def listar_historial_usuario(usuario_id, tipo, offset, limit):
        comprador_alias = aliased(Usuario)
        vendedor_alias = aliased(Usuario)
        calificacion_alias = aliased(Calificacion)

        query = db.session.query(
            Transaccion,
            Anuncio.titulo.label("anuncio_titulo"),
            Anuncio.categoria.label("anuncio_categoria"),
            Anuncio.subcategoria.label("anuncio_subcategoria"),
            Anuncio.precio.label("anuncio_precio"),
            MediaAnuncio.ruta_relativa.label("imagen_principal"),
            vendedor_alias.id.label("vendedor_public_id"),
            vendedor_alias.nombre.label("vendedor_nombre"),
            vendedor_alias.rol.label("vendedor_rol"),
            comprador_alias.id.label("comprador_public_id"),
            comprador_alias.nombre.label("comprador_nombre"),
            comprador_alias.rol.label("comprador_rol"),
            calificacion_alias.puntaje.label("calificacion_puntaje"),
            calificacion_alias.comentario.label("calificacion_comentario"),
            calificacion_alias.created_at.label("calificacion_created_at"),
        ).outerjoin(
            Anuncio,
            Anuncio.id == Transaccion.anuncio_id,
        ).outerjoin(
            MediaAnuncio,
            db.and_(
                MediaAnuncio.anuncio_id == Transaccion.anuncio_id,
                MediaAnuncio.tipo_media == "imagen",
                MediaAnuncio.es_principal.is_(True),
            ),
        ).join(
            vendedor_alias,
            vendedor_alias.id == Transaccion.vendedor_id,
        ).join(
            comprador_alias,
            comprador_alias.id == Transaccion.comprador_id,
        ).outerjoin(
            calificacion_alias,
            db.and_(
                calificacion_alias.transaccion_id == Transaccion.id,
                calificacion_alias.calificador_id == usuario_id,
            ),
        )

        if tipo == "ventas":
            query = query.filter(Transaccion.vendedor_id == usuario_id)
        elif tipo == "compras":
            query = query.filter(Transaccion.comprador_id == usuario_id)
        else:
            query = query.filter(
                db.or_(
                    Transaccion.vendedor_id == usuario_id,
                    Transaccion.comprador_id == usuario_id,
                )
            )

        query = query.order_by(Transaccion.created_at.desc(), Transaccion.id.desc())
        total = db.session.query(db.func.count()).select_from(query.order_by(None).subquery()).scalar()
        items = query.offset(offset).limit(limit).all()
        return items, total

    @staticmethod
    def contar_ventas_usuario(usuario_id):
        return Transaccion.query.filter_by(vendedor_id=usuario_id).count()

    @staticmethod
    def contar_compras_usuario(usuario_id):
        return Transaccion.query.filter_by(comprador_id=usuario_id).count()

    @staticmethod
    def contar_calificaciones_pendientes_usuario(usuario_id):
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
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
