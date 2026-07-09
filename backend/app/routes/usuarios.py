from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.usuario_controller import (
    actualizar_perfil_me_controller,
    historial_transacciones_me_controller,
    panel_usuario_me_controller,
    perfil_publico_usuario_controller,
)


usuarios_bp = Blueprint("usuarios", __name__)

usuarios_bp.add_url_rule(
    "/<usuario_id>/perfil",
    view_func=perfil_publico_usuario_controller,
    methods=["GET"],
)

usuarios_bp.add_url_rule(
    "/me/transacciones",
    view_func=jwt_required()(historial_transacciones_me_controller),
    methods=["GET"],
)

usuarios_bp.add_url_rule(
    "/me/panel",
    view_func=jwt_required()(panel_usuario_me_controller),
    methods=["GET"],
)

usuarios_bp.add_url_rule(
    "/me/perfil",
    view_func=jwt_required()(actualizar_perfil_me_controller),
    methods=["PATCH"],
)
