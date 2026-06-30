from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.anuncio_controller import (
    desactivar_anuncio_controller,
    editar_anuncio_controller,
    eliminar_media_controller,
    feed_anuncios_controller,
    marcar_vendido_controller,
    publicar_anuncio_controller,
    reactivar_anuncio_controller,
    reordenar_media_controller,
    reemplazar_media_controller,
    subir_media_controller,
)


anuncios_bp = Blueprint("anuncios", __name__)

anuncios_bp.add_url_rule(
    "",
    view_func=feed_anuncios_controller,
    methods=["GET"],
)

anuncios_bp.add_url_rule(
    "",
    view_func=jwt_required()(publicar_anuncio_controller),
    methods=["POST"],
)

anuncios_bp.add_url_rule(
    "/<int:anuncio_id>/media",
    view_func=jwt_required()(subir_media_controller),
    methods=["POST"],
)

anuncios_bp.add_url_rule(
    "/<int:anuncio_id>",
    view_func=jwt_required()(editar_anuncio_controller),
    methods=["PATCH"],
)

anuncios_bp.add_url_rule(
    "/<int:anuncio_id>/vendido",
    view_func=jwt_required()(marcar_vendido_controller),
    methods=["PATCH"],
)

anuncios_bp.add_url_rule(
    "/<int:anuncio_id>/desactivar",
    view_func=jwt_required()(desactivar_anuncio_controller),
    methods=["PATCH"],
)

anuncios_bp.add_url_rule(
    "/<int:anuncio_id>/reactivar",
    view_func=jwt_required()(reactivar_anuncio_controller),
    methods=["PATCH"],
)

anuncios_bp.add_url_rule(
    "/<int:anuncio_id>/media/orden",
    view_func=jwt_required()(reordenar_media_controller),
    methods=["PATCH"],
)

anuncios_bp.add_url_rule(
    "/<int:anuncio_id>/media/<int:media_id>",
    view_func=jwt_required()(eliminar_media_controller),
    methods=["DELETE"],
)

anuncios_bp.add_url_rule(
    "/<int:anuncio_id>/media/<int:media_id>",
    view_func=jwt_required()(reemplazar_media_controller),
    methods=["PUT"],
)
