from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.anuncio_controller import (
    publicar_anuncio_controller,
    subir_media_controller,
)


anuncios_bp = Blueprint("anuncios", __name__)

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
