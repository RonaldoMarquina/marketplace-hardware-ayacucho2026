from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from app.models.anuncio import Anuncio
from app.models.media_anuncio import MediaAnuncio
from app.repositories.anuncio_repository import AnuncioRepository
from app.utils.media_validation import MediaValidationError, classify_media, validate_and_store_media


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

    @staticmethod
    def subir_media(anuncio_id, usuario_id, files, upload_folder):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return {
                "success": False,
                "data": {},
                "error": "NOT_FOUND",
                "message": "Anuncio no encontrado.",
            }

        if anuncio.usuario_id != usuario_id:
            return {
                "success": False,
                "data": {},
                "error": "FORBIDDEN",
                "message": "El anuncio no pertenece al usuario autenticado.",
            }

        archivos = [file for file in files if file and file.filename]
        if not archivos:
            return {
                "success": False,
                "data": {},
                "error": "MISSING_FILE",
                "message": "Debe adjuntar al menos un archivo.",
            }

        try:
            tipos = [classify_media(file)[0] for file in archivos]
        except MediaValidationError as error:
            return _media_error_response(error)

        imagenes_request = tipos.count("imagen")
        videos_request = tipos.count("video")
        if imagenes_request > 8:
            return {
                "success": False,
                "data": {},
                "error": "TOO_MANY_FILES",
                "message": "No se permiten mas de 8 imagenes por peticion.",
            }
        if videos_request > 1:
            return {
                "success": False,
                "data": {},
                "error": "TOO_MANY_FILES",
                "message": "No se permite mas de 1 video por peticion.",
            }

        imagenes_existentes = AnuncioRepository.contar_media(anuncio_id, "imagen")
        videos_existentes = AnuncioRepository.contar_media(anuncio_id, "video")
        if imagenes_existentes + imagenes_request > 5:
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "El anuncio ya alcanzo el limite de 5 imagenes.",
            }
        if videos_existentes + videos_request > 1:
            return {
                "success": False,
                "data": {},
                "error": "CONFLICT",
                "message": "El anuncio ya tiene un video registrado.",
            }

        media_creada = []
        archivos_guardados = []
        siguiente_orden = AnuncioRepository.obtener_siguiente_orden_imagen(anuncio_id)
        primera_imagen = imagenes_existentes == 0

        try:
            for file in archivos:
                tipo_media, ruta_relativa, ruta_absoluta = validate_and_store_media(
                    file,
                    upload_folder,
                    anuncio_id,
                )
                archivos_guardados.append(ruta_absoluta)

                es_imagen = tipo_media == "imagen"
                media = MediaAnuncio(
                    anuncio_id=anuncio_id,
                    tipo_media=tipo_media,
                    ruta_relativa=ruta_relativa,
                    es_principal=bool(es_imagen and primera_imagen),
                    orden=siguiente_orden if es_imagen else None,
                )
                AnuncioRepository.agregar_media(media)
                media_creada.append(media)

                if es_imagen:
                    primera_imagen = False
                    siguiente_orden += 1

            AnuncioRepository.commit()
            return {
                "success": True,
                "data": {"media": [media.to_public_dict() for media in media_creada]},
                "error": None,
                "message": "Media cargada correctamente.",
            }
        except MediaValidationError as error:
            AnuncioRepository.rollback()
            _eliminar_archivos(archivos_guardados)
            return _media_error_response(error)
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            _eliminar_archivos(archivos_guardados)
            return {
                "success": False,
                "data": {},
                "error": "DATABASE_ERROR",
                "message": "No se pudo registrar la media del anuncio.",
            }


def _media_error_response(error):
    return {
        "success": False,
        "data": {},
        "error": error.error_code,
        "message": error.message,
    }


def _eliminar_archivos(paths):
    for path in paths:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            pass
