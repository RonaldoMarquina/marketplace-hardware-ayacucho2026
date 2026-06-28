from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename


ALLOWED_DOCUMENT_SIGNATURES = {
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    "png": (b"\x89PNG\r\n\x1a\n",),
}


class FileValidationError(Exception):
    def __init__(self, message, status_code=415, error_code="INVALID_FILE"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


def validate_store_document(file_storage, upload_folder, max_size_bytes):
    if not file_storage or not file_storage.filename:
        raise FileValidationError(
            "El documento de identidad es obligatorio.",
            status_code=400,
            error_code="MISSING_FILE",
        )

    original_name = secure_filename(file_storage.filename)
    extension = Path(original_name).suffix.lower().lstrip(".")
    if extension not in ALLOWED_DOCUMENT_SIGNATURES:
        raise FileValidationError(
            "Formato de archivo no permitido.",
            status_code=415,
            error_code="INVALID_FILE_TYPE",
        )

    stream = file_storage.stream
    current_position = stream.tell()
    stream.seek(0, 2)
    file_size = stream.tell()
    stream.seek(0)

    if file_size > max_size_bytes:
        stream.seek(current_position)
        raise FileValidationError(
            "El documento supera el tamano maximo permitido.",
            status_code=413,
            error_code="FILE_TOO_LARGE",
        )

    header = stream.read(16)
    stream.seek(0)
    if not any(
        header.startswith(signature)
        for signature in ALLOWED_DOCUMENT_SIGNATURES[extension]
    ):
        stream.seek(current_position)
        raise FileValidationError(
            "El contenido del archivo no coincide con un JPG o PNG valido.",
            status_code=415,
            error_code="INVALID_FILE_TYPE",
        )

    filename = f"{uuid4().hex}.{extension}"
    relative_path = Path("uploads") / "tiendas" / filename
    absolute_folder = Path(upload_folder) / "tiendas"
    absolute_folder.mkdir(parents=True, exist_ok=True)
    absolute_path = absolute_folder / filename
    file_storage.save(absolute_path)

    return str(relative_path).replace("\\", "/"), absolute_path
