from flask import Blueprint

from app.controllers.auth_controller import (
    forgot_password_controller,
    login_controller,
    reenviar_verificacion_controller,
    registrar_tienda_controller,
    registrar_usuario_controller,
    reset_password_controller,
    verificar_correo_controller,
)


auth_bp = Blueprint("auth", __name__)

auth_bp.add_url_rule(
    "/register",
    view_func=registrar_usuario_controller,
    methods=["POST"],
)

auth_bp.add_url_rule(
    "/register/tienda",
    view_func=registrar_tienda_controller,
    methods=["POST"],
)

auth_bp.add_url_rule(
    "/login",
    view_func=login_controller,
    methods=["POST"],
)

auth_bp.add_url_rule(
    "/verify-email",
    view_func=verificar_correo_controller,
    methods=["GET"],
)

auth_bp.add_url_rule(
    "/verify-email/resend",
    view_func=reenviar_verificacion_controller,
    methods=["POST"],
)

auth_bp.add_url_rule(
    "/password/forgot",
    view_func=forgot_password_controller,
    methods=["POST"],
)

auth_bp.add_url_rule(
    "/password/reset",
    view_func=reset_password_controller,
    methods=["POST"],
)
