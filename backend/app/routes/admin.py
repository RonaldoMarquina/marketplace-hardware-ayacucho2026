from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.admin_controller import (
    bloquear_anuncio_admin_controller,
    desbloquear_anuncio_admin_controller,
    historial_moderacion_controller,
    listar_anuncios_reportados_controller,
)
from app.utils.auth import check_admin_role


admin_bp = Blueprint("admin", __name__)

admin_bp.add_url_rule(
    "/anuncios/reportados",
    view_func=jwt_required()(check_admin_role()(listar_anuncios_reportados_controller)),
    methods=["GET"],
)

admin_bp.add_url_rule(
    "/anuncios/<int:anuncio_id>/bloquear",
    view_func=jwt_required()(check_admin_role()(bloquear_anuncio_admin_controller)),
    methods=["PATCH"],
)

admin_bp.add_url_rule(
    "/anuncios/<int:anuncio_id>/desbloquear",
    view_func=jwt_required()(check_admin_role()(desbloquear_anuncio_admin_controller)),
    methods=["PATCH"],
)

admin_bp.add_url_rule(
    "/moderacion/historial",
    view_func=jwt_required()(check_admin_role()(historial_moderacion_controller)),
    methods=["GET"],
)
