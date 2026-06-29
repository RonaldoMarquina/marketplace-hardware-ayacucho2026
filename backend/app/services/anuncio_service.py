from sqlalchemy.exc import SQLAlchemyError

from app.models.anuncio import Anuncio
from app.repositories.anuncio_repository import AnuncioRepository


class AnuncioService:
    @staticmethod
    def publicar_anuncio(usuario_id, data):
        # El usuario_id viene del JWT, nunca del body. Esta regla evita que un
        # cliente publique anuncios a nombre de otra cuenta.
        usuario = AnuncioRepository.buscar_usuario_por_id(usuario_id)
        if not usuario:
            return {
                "success": False,
                "data": {},
                "error": "NOT_FOUND",
                "message": "Usuario no encontrado.",
            }

        if usuario.estado != "ACTIVO":
            return {
                "success": False,
                "data": {},
                "error": "FORBIDDEN",
                "message": "La cuenta debe estar activa para publicar anuncios.",
            }

        if usuario.rol == "TIENDA_VERIFICADA":
            tienda = getattr(usuario, "tienda", None)
            if tienda and tienda.estado != "ACTIVO":
                return {
                    "success": False,
                    "data": {},
                    "error": "FORBIDDEN",
                    "message": "La tienda debe estar activa para publicar anuncios.",
                }

        if usuario.rol == "USER_ESTANDAR":
            activos = AnuncioRepository.contar_anuncios_activos(usuario.id)
            if activos >= 25:
                return {
                    "success": False,
                    "data": {},
                    "error": "FORBIDDEN",
                    "message": "El usuario estandar alcanzo el limite de 25 anuncios activos.",
                }

        anuncio = Anuncio(
            usuario_id=usuario.id,
            titulo=data["titulo"],
            descripcion=data["descripcion"],
            categoria=data["categoria"],
            subcategoria=data["subcategoria"],
            condicion=data["condicion"],
            precio=data["precio"],
            especificaciones=data.get("especificaciones"),
            estado="ACTIVO",
        )

        try:
            AnuncioRepository.agregar(anuncio)
            AnuncioRepository.commit()
            return {
                "success": True,
                "data": anuncio.to_public_dict(),
                "error": None,
                "message": "Anuncio publicado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return {
                "success": False,
                "data": {},
                "error": "DATABASE_ERROR",
                "message": "No se pudo publicar el anuncio.",
            }
