from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename


IMAGE_SIGNATURES = {
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    "png": (b"\x89PNG\r\n\x1a\n",),
    "webp": (b"RIFF",),
    "avif": (b"\x00\x00\x00",),
}

VIDEO_SIGNATURES = {
    "mp4": (b"\x00\x00\x00",),
}

IMAGE_EXTENSIONS = frozenset(IMAGE_SIGNATURES.keys())
VIDEO_EXTENSIONS = frozenset(VIDEO_SIGNATURES.keys())

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 40 * 1024 * 1024


class MediaValidationError(Exception):
    def __init__(self, message, status_code=422, error_code="INVALID_FILE_TYPE"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


def classify_media(file_storage):
    if not file_storage or not file_storage.filename:
        raise MediaValidationError(
            "Archivo invalido.",
            status_code=400,
            error_code="MISSING_FILE",
        )

    filename = secure_filename(file_storage.filename)
    extension = Path(filename).suffix.lower().lstrip(".")
    if extension in IMAGE_EXTENSIONS:
        return "imagen", extension
    if extension in VIDEO_EXTENSIONS:
        return "video", extension

    raise MediaValidationError(
        "Tipo de archivo no permitido.",
        status_code=422,
        error_code="INVALID_FILE_TYPE",
    )


def validate_and_store_media(file_storage, upload_folder, anuncio_id):
    tipo_media, extension, _file_size = validate_media_file(file_storage)
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    filename = f"{uuid4().hex}-{timestamp}.{extension}"
    relative_path = Path("uploads") / "anuncios" / str(anuncio_id) / filename
    absolute_folder = Path(upload_folder) / "anuncios" / str(anuncio_id)
    absolute_folder.mkdir(parents=True, exist_ok=True)
    absolute_path = absolute_folder / filename
    file_storage.save(absolute_path)

    return tipo_media, str(relative_path).replace("\\", "/"), absolute_path


def validate_media_file(file_storage):
    tipo_media, extension = classify_media(file_storage)
    max_size = MAX_IMAGE_SIZE if tipo_media == "imagen" else MAX_VIDEO_SIZE

    stream = file_storage.stream
    current_position = stream.tell()
    stream.seek(0, 2)
    file_size = stream.tell()
    stream.seek(0)

    if file_size > max_size:
        stream.seek(current_position)
        raise MediaValidationError(
            "El archivo supera el tamano maximo permitido.",
            status_code=413,
            error_code="FILE_TOO_LARGE",
        )

    header = stream.read(32)
    stream.seek(0)
    if not _valid_real_signature(header, extension, tipo_media):
        stream.seek(current_position)
        raise MediaValidationError(
            "El contenido del archivo no coincide con el formato permitido.",
            status_code=422,
            error_code="INVALID_FILE_TYPE",
        )

    return tipo_media, extension, file_size


def _valid_real_signature(header, extension, tipo_media):
    if tipo_media == "imagen" and extension == "webp":
        return header.startswith(b"RIFF") and header[8:12] == b"WEBP"

    if tipo_media == "imagen" and extension == "avif":
        return len(header) >= 12 and header[4:8] == b"ftyp" and header[8:12] in {
            b"avif",
            b"avis",
        }

    if tipo_media == "video" and extension == "mp4":
        return len(header) >= 12 and header[4:8] == b"ftyp"

    signatures = IMAGE_SIGNATURES.get(extension, ())
    return any(header.startswith(signature) for signature in signatures)
