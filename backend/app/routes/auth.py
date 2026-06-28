from flask import Blueprint

from app.controllers.auth_controller import (
    registrar_tienda_controller,
    registrar_usuario_controller,
)


# La capa routes solo declara endpoints y los conecta con controllers.
# El prefijo /api/v1/auth se registra en create_app() para centralizar versionado.
auth_bp = Blueprint("auth", __name__)

# HU-01: POST /api/v1/auth/register
auth_bp.add_url_rule(
    "/register",
    view_func=registrar_usuario_controller,
    methods=["POST"],
)

# HU-02: POST /api/v1/auth/register/tienda
auth_bp.add_url_rule(
    "/register/tienda",
    view_func=registrar_tienda_controller,
    methods=["POST"],
)
