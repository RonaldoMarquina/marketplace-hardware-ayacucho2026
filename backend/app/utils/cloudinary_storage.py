from datetime import UTC, datetime
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from flask import current_app

from app.utils.media_validation import MediaValidationError, validate_media_file


class CloudinaryStorageError(Exception):
    def __init__(
        self,
        message,
        status_code=500,
        error_code="CLOUDINARY_UPLOAD_FAILED",
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


def init_cloudinary(app):
    if not app.config.get("CLOUDINARY_ENABLED"):
        app.extensions["cloudinary_configured"] = False
        return

    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )
    app.extensions["cloudinary_configured"] = True


def upload_media_to_cloudinary(file_storage, anuncio_id):
    if not current_app.config.get("CLOUDINARY_ENABLED"):
        raise CloudinaryStorageError(
            "Cloudinary no esta configurado para esta instancia.",
            status_code=500,
            error_code="CLOUDINARY_NOT_CONFIGURED",
        )

    tipo_media, _extension, _file_size = validate_media_file(file_storage)
    resource_type = "image" if tipo_media == "imagen" else "video"

    try:
        file_storage.stream.seek(0)
        upload_result = cloudinary.uploader.upload(
            file_storage.stream,
            asset_folder=_build_asset_folder(current_app.config["CLOUDINARY_FOLDER"], anuncio_id),
            public_id=_build_public_id(tipo_media),
            resource_type=resource_type,
            overwrite=False,
        )
        file_storage.stream.seek(0)
    except Exception as error:
        raise CloudinaryStorageError(
            "No se pudo cargar el archivo en Cloudinary.",
            status_code=502,
            error_code="CLOUDINARY_UPLOAD_FAILED",
        ) from error

    secure_url = upload_result.get("secure_url")
    public_id = upload_result.get("public_id")
    if not secure_url or not public_id:
        raise CloudinaryStorageError(
            "Cloudinary no devolvio los metadatos minimos esperados.",
            status_code=502,
            error_code="CLOUDINARY_INVALID_RESPONSE",
        )

    return {
        "tipo_media": tipo_media,
        "ruta_relativa": secure_url,
        "public_id": public_id,
        "resource_type": upload_result.get("resource_type", resource_type),
        "format": upload_result.get("format"),
        "bytes": upload_result.get("bytes"),
        "width": upload_result.get("width"),
        "height": upload_result.get("height"),
        "version": upload_result.get("version"),
    }


def delete_media_from_cloudinary(public_id, resource_type):
    if not public_id:
        return {"result": "not_configured"}

    if not current_app.config.get("CLOUDINARY_ENABLED"):
        raise CloudinaryStorageError(
            "Cloudinary no esta configurado para esta instancia.",
            status_code=500,
            error_code="CLOUDINARY_NOT_CONFIGURED",
        )

    try:
        return cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type or "image",
            invalidate=True,
        )
    except Exception as error:
        raise CloudinaryStorageError(
            "No se pudo eliminar el archivo en Cloudinary.",
            status_code=502,
            error_code="CLOUDINARY_DELETE_FAILED",
        ) from error


def _build_asset_folder(base_folder, anuncio_id):
    normalized_base = (base_folder or "hardware-ayacucho").strip().strip("/")
    return f"{normalized_base}/{anuncio_id}"


def _build_public_id(tipo_media):
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    return f"{tipo_media}-{uuid4().hex}-{timestamp}"
