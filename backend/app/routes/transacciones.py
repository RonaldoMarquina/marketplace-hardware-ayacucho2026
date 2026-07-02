from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.transaccion_controller import calificar_comprador_controller, calificar_vendedor_controller


transacciones_bp = Blueprint("transacciones", __name__)

transacciones_bp.add_url_rule(
    "/<int:transaccion_id>/calificar/vendedor",
    view_func=jwt_required()(calificar_vendedor_controller),
    methods=["POST"],
)

transacciones_bp.add_url_rule(
    "/<int:transaccion_id>/calificar/comprador",
    view_func=jwt_required()(calificar_comprador_controller),
    methods=["POST"],
)
