from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app.repositories.anuncio_repository import AnuncioRepository


def check_admin_role():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            try:
                usuario_id = int(get_jwt_identity())
            except (TypeError, ValueError):
                return jsonify({
                    "success": False,
                    "data": {},
                    "error": "FORBIDDEN",
                    "message": "Acceso restringido a administradores activos.",
                }), 403

            usuario = AnuncioRepository.buscar_usuario_por_id(usuario_id)
            if not usuario or usuario.rol != "ADMIN" or usuario.estado != "ACTIVO":
                return jsonify({
                    "success": False,
                    "data": {},
                    "error": "FORBIDDEN",
                    "message": "Acceso restringido a administradores activos.",
                }), 403

            return view_func(*args, **kwargs)

        return wrapper

    return decorator
