from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.anuncio_controller import publicar_anuncio_controller


anuncios_bp = Blueprint("anuncios", __name__)

# HU-05: publicar anuncio. La proteccion JWT se declara en la ruta.
anuncios_bp.add_url_rule(
    "",
    view_func=jwt_required()(publicar_anuncio_controller),
    methods=["POST"],
)
