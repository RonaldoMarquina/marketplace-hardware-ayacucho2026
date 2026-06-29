from copy import deepcopy
from pathlib import Path

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.models.anuncio import SUBCATEGORIAS_POR_CATEGORIA, Anuncio
from app.models.media_anuncio import MediaAnuncio
from app.repositories.anuncio_repository import AnuncioRepository
from app.utils.media_validation import MediaValidationError, classify_media, validate_and_store_media


EDITABLE_FIELDS = {
    "titulo",
    "categoria",
    "subcategoria",
    "descripcion",
    "condicion",
    "precio",
    "especificaciones",
}

MAX_REACTIVACIONES = 3


class AnuncioService:
    @staticmethod
    def publicar_anuncio(usuario_id, data):
        # El usuario_id viene del JWT, nunca del body. Esta regla evita que un
        # cliente publique anuncios a nombre de otra cuenta.
        usuario = AnuncioRepository.buscar_usuario_por_id(usuario_id)
        if not usuario:
            return _error_response("NOT_FOUND", "Usuario no encontrado.")

        if usuario.estado != "ACTIVO":
            return _error_response("FORBIDDEN", "La cuenta debe estar activa para publicar anuncios.")

        if usuario.rol == "TIENDA_VERIFICADA":
            tienda = getattr(usuario, "tienda", None)
            if tienda and tienda.estado != "ACTIVO":
                return _error_response("FORBIDDEN", "La tienda debe estar activa para publicar anuncios.")

        if usuario.rol == "USER_ESTANDAR":
            activos = AnuncioRepository.contar_anuncios_activos(usuario.id)
            if activos >= 25:
                return _error_response(
                    "FORBIDDEN",
                    "El usuario estandar alcanzo el limite de 25 anuncios activos.",
                )

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
            reactivaciones_count=0,
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
            return _error_response("DATABASE_ERROR", "No se pudo publicar el anuncio.")

    @staticmethod
    def editar_anuncio(anuncio_id, usuario_id, data):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_edicion(anuncio)
        if status_error:
            return status_error

        cambios = {campo: valor for campo, valor in data.items() if campo in EDITABLE_FIELDS}
        if not cambios:
            return _error_response("EMPTY_BODY", "Debe enviar al menos un campo editable.")

        if "categoria" in cambios and "subcategoria" not in cambios:
            return _error_response(
                "VALIDATION_ERROR",
                "La categoria requiere subcategoria en el mismo request.",
                {"subcategoria": ["La subcategoria es obligatoria al cambiar categoria."]},
            )

        categoria_objetivo = cambios.get("categoria", anuncio.categoria)
        subcategoria_objetivo = cambios.get("subcategoria", anuncio.subcategoria)
        if "subcategoria" in cambios and subcategoria_objetivo not in SUBCATEGORIAS_POR_CATEGORIA.get(categoria_objetivo, ()):
            return _error_response(
                "VALIDATION_ERROR",
                "La subcategoria no corresponde a la categoria seleccionada.",
                {"subcategoria": ["La subcategoria no corresponde a la categoria seleccionada."]},
            )

        if "especificaciones" in cambios:
            cambios["especificaciones"] = _json_merge_patch(anuncio.especificaciones, cambios["especificaciones"])

        try:
            campos_modificados = []
            for campo, valor in cambios.items():
                setattr(anuncio, campo, valor)
                campos_modificados.append(campo)

            AnuncioRepository.commit()
            current_app.logger.info(
                "HU-07 editar anuncio usuario_id=%s anuncio_id=%s campos=%s",
                usuario_id,
                anuncio_id,
                ",".join(campos_modificados),
            )
            return {
                "success": True,
                "data": anuncio.to_public_dict(),
                "error": None,
                "message": "Anuncio actualizado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo actualizar el anuncio.")

    @staticmethod
    def desactivar_anuncio(anuncio_id, usuario_id):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_para_desactivar(anuncio)
        if status_error:
            return status_error

        try:
            anuncio.estado = "INACTIVO"
            AnuncioRepository.commit()
            current_app.logger.info(
                "HU-07 desactivar anuncio usuario_id=%s anuncio_id=%s",
                usuario_id,
                anuncio_id,
            )
            return {
                "success": True,
                "data": {
                    "id": anuncio.id,
                    "estado": anuncio.estado,
                    "updated_at": anuncio.updated_at.isoformat() if anuncio.updated_at else None,
                },
                "error": None,
                "message": "Anuncio desactivado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo desactivar el anuncio.")

    @staticmethod
    def reactivar_anuncio(anuncio_id, usuario_id):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_para_reactivar(anuncio)
        if status_error:
            return status_error

        if anuncio.reactivaciones_count >= MAX_REACTIVACIONES:
            return _error_response("FORBIDDEN", "El anuncio alcanzo el limite de 3 reactivaciones.")

        try:
            anuncio.estado = "ACTIVO"
            anuncio.reactivaciones_count += 1
            AnuncioRepository.commit()
            current_app.logger.info(
                "HU-07 reactivar anuncio usuario_id=%s anuncio_id=%s reactivaciones_count=%s",
                usuario_id,
                anuncio_id,
                anuncio.reactivaciones_count,
            )
            return {
                "success": True,
                "data": {
                    "id": anuncio.id,
                    "estado": anuncio.estado,
                    "reactivaciones_count": anuncio.reactivaciones_count,
                    "reactivaciones_restantes": MAX_REACTIVACIONES - anuncio.reactivaciones_count,
                    "updated_at": anuncio.updated_at.isoformat() if anuncio.updated_at else None,
                },
                "error": None,
                "message": "Anuncio reactivado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo reactivar el anuncio.")

    @staticmethod
    def subir_media(anuncio_id, usuario_id, files, upload_folder):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        archivos = [file for file in files if file and file.filename]
        if not archivos:
            return _error_response("MISSING_FILE", "Debe adjuntar al menos un archivo.")

        try:
            tipos = [classify_media(file)[0] for file in archivos]
        except MediaValidationError as error:
            return _media_error_response(error)

        imagenes_request = tipos.count("imagen")
        videos_request = tipos.count("video")
        if imagenes_request > 8:
            return _error_response("TOO_MANY_FILES", "No se permiten mas de 8 imagenes por peticion.")
        if videos_request > 1:
            return _error_response("TOO_MANY_FILES", "No se permite mas de 1 video por peticion.")

        imagenes_existentes = AnuncioRepository.contar_media(anuncio_id, "imagen")
        videos_existentes = AnuncioRepository.contar_media(anuncio_id, "video")
        if imagenes_existentes + imagenes_request > 8:
            return _error_response("CONFLICT", "El anuncio ya alcanzo el limite de 8 imagenes.")
        if videos_existentes + videos_request > 1:
            return _error_response("CONFLICT", "El anuncio ya tiene un video registrado.")

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
            return _error_response("DATABASE_ERROR", "No se pudo registrar la media del anuncio.")

    @staticmethod
    def reordenar_media(anuncio_id, usuario_id, ordered_media_ids):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_operacion_media(anuncio)
        if status_error:
            return status_error

        media_items = AnuncioRepository.listar_media_por_anuncio(anuncio_id)
        imagenes = [media for media in media_items if media.tipo_media == "imagen"]
        videos = [media for media in media_items if media.tipo_media == "video"]

        image_ids = [media.id for media in imagenes]
        video_ids = {media.id for media in videos}
        received_ids = list(ordered_media_ids)

        if any(media_id in video_ids for media_id in received_ids):
            return _error_response("VALIDATION_ERROR", "El array orden no puede incluir videos.")

        if len(received_ids) != len(set(received_ids)):
            return _error_response("VALIDATION_ERROR", "El array orden contiene IDs repetidos.")

        if set(received_ids) != set(image_ids):
            return _error_response(
                "VALIDATION_ERROR",
                "El array orden debe incluir todos los IDs de imagen del anuncio sin omitir ni agregar ajenos.",
            )

        image_by_id = {media.id: media for media in imagenes}
        try:
            for posicion, media_id in enumerate(received_ids):
                media = image_by_id[media_id]
                media.orden = posicion
                media.es_principal = posicion == 0

            AnuncioRepository.commit()
            return {
                "success": True,
                "data": {
                    "media": [image_by_id[media_id].to_public_dict() for media_id in received_ids],
                },
                "error": None,
                "message": "Orden de imagenes actualizado correctamente.",
            }
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo reordenar la media.")

    @staticmethod
    def eliminar_media(anuncio_id, media_id, usuario_id, upload_folder):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_operacion_media(anuncio)
        if status_error:
            return status_error

        media = AnuncioRepository.buscar_media_de_anuncio(anuncio_id, media_id)
        if not media:
            return _error_response("NOT_FOUND", "Media no encontrada para el anuncio.")

        imagenes_restantes = [
            item for item in AnuncioRepository.listar_imagenes_por_anuncio(anuncio_id)
            if item.id != media.id
        ]
        _reindexar_imagenes(imagenes_restantes)

        absolute_path = _absolute_media_path(upload_folder, media.ruta_relativa)
        eliminado = {"id": media.id, "tipo_media": media.tipo_media}

        try:
            AnuncioRepository.eliminar_media(media)
            AnuncioRepository.flush()
            absolute_path.unlink()
            AnuncioRepository.commit()
            return {
                "success": True,
                "data": {
                    "eliminado": eliminado,
                    "media_restante": [item.to_public_dict() for item in imagenes_restantes],
                },
                "error": None,
                "message": "Media eliminada correctamente.",
            }
        except FileNotFoundError:
            AnuncioRepository.rollback()
            return _error_response("FILE_DELETE_ERROR", "No se pudo eliminar el archivo fisico asociado.")
        except OSError:
            AnuncioRepository.rollback()
            return _error_response("FILE_DELETE_ERROR", "No se pudo eliminar el archivo fisico asociado.")
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            return _error_response("DATABASE_ERROR", "No se pudo eliminar la media.")

    @staticmethod
    def reemplazar_media(anuncio_id, media_id, usuario_id, file_storage, upload_folder):
        anuncio = AnuncioRepository.buscar_anuncio_por_id(anuncio_id)
        if not anuncio:
            return _error_response("NOT_FOUND", "Anuncio no encontrado.")

        ownership_error = _validar_propietario(anuncio, usuario_id)
        if ownership_error:
            return ownership_error

        status_error = _validar_estado_operacion_media(anuncio)
        if status_error:
            return status_error

        media = AnuncioRepository.buscar_media_de_anuncio(anuncio_id, media_id)
        if not media:
            return _error_response("NOT_FOUND", "Media no encontrada para el anuncio.")

        if not file_storage or not file_storage.filename:
            return _error_response("MISSING_FILE", "Debe adjuntar un archivo.")

        try:
            nuevo_tipo, ruta_relativa, ruta_absoluta = validate_and_store_media(
                file_storage,
                upload_folder,
                anuncio_id,
            )
        except MediaValidationError as error:
            return _media_error_response(error)

        if nuevo_tipo != media.tipo_media:
            _eliminar_archivos([ruta_absoluta])
            return _error_response(
                "INVALID_FILE_TYPE",
                "El archivo nuevo debe ser del mismo tipo de media que el original.",
            )

        ruta_anterior = media.ruta_relativa
        absolute_old_path = _absolute_media_path(upload_folder, ruta_anterior)

        try:
            media.ruta_relativa = ruta_relativa
            AnuncioRepository.commit()
        except SQLAlchemyError:
            AnuncioRepository.rollback()
            _eliminar_archivos([ruta_absoluta])
            return _error_response("DATABASE_ERROR", "No se pudo reemplazar la media.")

        try:
            absolute_old_path.unlink(missing_ok=False)
        except OSError:
            current_app.logger.warning(
                "No se pudo eliminar archivo previo de media anuncio_id=%s media_id=%s ruta=%s",
                anuncio_id,
                media_id,
                ruta_anterior,
            )

        return {
            "success": True,
            "data": media.to_public_dict(),
            "error": None,
            "message": "Media reemplazada correctamente.",
        }


def _error_response(error_code, message, data=None):
    return {
        "success": False,
        "data": data or {},
        "error": error_code,
        "message": message,
    }


def _validar_propietario(anuncio, usuario_id):
    if anuncio.usuario_id != usuario_id:
        return _error_response("FORBIDDEN", "El anuncio no pertenece al usuario autenticado.")
    return None


def _validar_estado_edicion(anuncio):
    if anuncio.estado == "BLOQUEADO":
        return _error_response("FORBIDDEN", "El anuncio se encuentra bloqueado.")
    if anuncio.estado == "VENDIDO":
        return _error_response("CONFLICT", "El anuncio vendido no puede modificarse.")
    if anuncio.estado == "INACTIVO":
        return _error_response("CONFLICT", "El anuncio inactivo no puede modificarse.")
    return None


def _validar_estado_para_desactivar(anuncio):
    if anuncio.estado == "BLOQUEADO":
        return _error_response("FORBIDDEN", "El anuncio se encuentra bloqueado.")
    if anuncio.estado == "VENDIDO":
        return _error_response("CONFLICT", "El anuncio vendido no puede desactivarse.")
    if anuncio.estado == "INACTIVO":
        return _error_response("CONFLICT", "El anuncio ya se encuentra inactivo.")
    return None


def _validar_estado_para_reactivar(anuncio):
    if anuncio.estado == "BLOQUEADO":
        return _error_response("FORBIDDEN", "El anuncio se encuentra bloqueado.")
    if anuncio.estado == "VENDIDO":
        return _error_response("CONFLICT", "El anuncio vendido no puede reactivarse.")
    if anuncio.estado == "ACTIVO":
        return _error_response("CONFLICT", "El anuncio ya se encuentra activo.")
    return None


def _validar_estado_operacion_media(anuncio):
    if anuncio.estado == "BLOQUEADO":
        return _error_response("FORBIDDEN", "El anuncio se encuentra bloqueado.")
    if anuncio.estado == "VENDIDO":
        return _error_response("CONFLICT", "El anuncio vendido no permite cambios de media.")
    if anuncio.estado == "INACTIVO":
        return _error_response("CONFLICT", "El anuncio inactivo no permite cambios de media.")
    return None


def _media_error_response(error):
    return _error_response(error.error_code, error.message)


def _eliminar_archivos(paths):
    for path in paths:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            pass


def _json_merge_patch(current_value, patch_value):
    # Replica el comportamiento de JSON_MERGE_PATCH para conservar claves no
    # enviadas y borrar las que lleguen explicitamente en null.
    if patch_value is None:
        return None

    if not isinstance(patch_value, dict):
        return deepcopy(patch_value)

    base = deepcopy(current_value) if isinstance(current_value, dict) else {}
    for key, value in patch_value.items():
        if value is None:
            base.pop(key, None)
            continue

        if isinstance(value, dict):
            base[key] = _json_merge_patch(base.get(key), value)
            continue

        base[key] = deepcopy(value)

    return base


def _reindexar_imagenes(imagenes):
    for posicion, image in enumerate(imagenes):
        image.orden = posicion
        image.es_principal = posicion == 0


def _absolute_media_path(upload_folder, relative_path):
    normalized = Path(relative_path)
    if normalized.parts and normalized.parts[0] == "uploads":
        normalized = Path(*normalized.parts[1:])
    return Path(upload_folder) / normalized
