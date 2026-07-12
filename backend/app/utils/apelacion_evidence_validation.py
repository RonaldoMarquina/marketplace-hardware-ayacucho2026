from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename


APPEAL_EVIDENCE_SIGNATURES = {
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    "png": (b"\x89PNG\r\n\x1a\n",),
}

MAX_APPEAL_EVIDENCES = 3
MAX_APPEAL_EVIDENCE_SIZE = 5 * 1024 * 1024


class AppealEvidenceValidationError(Exception):
    def __init__(self, message, status_code=422, error_code="INVALID_APPEAL_EVIDENCE"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


def validate_appeal_evidences(files, upload_folder, apelacion_id):
    files = [file_storage for file_storage in files if file_storage and file_storage.filename]
    if not files:
        return []

    if len(files) > MAX_APPEAL_EVIDENCES:
        raise AppealEvidenceValidationError(
            f"Solo se permiten hasta {MAX_APPEAL_EVIDENCES} evidencias por apelacion.",
            status_code=422,
            error_code="TOO_MANY_APPEAL_EVIDENCES",
        )

    validated = []
    for file_storage in files:
        validated.append(_validate_single_appeal_evidence(file_storage, upload_folder, apelacion_id))
    return validated


def persist_appeal_evidences(validated_files):
    for item in validated_files:
        item["absolute_path"].parent.mkdir(parents=True, exist_ok=True)
        item["file_storage"].stream.seek(0)
        item["file_storage"].save(item["absolute_path"])


def delete_appeal_evidences(validated_files):
    for item in validated_files:
        try:
            item["absolute_path"].unlink(missing_ok=True)
        except OSError:
            pass


def _validate_single_appeal_evidence(file_storage, upload_folder, apelacion_id):
    original_name = secure_filename(file_storage.filename)
    extension = Path(original_name).suffix.lower().lstrip(".")
    if extension not in APPEAL_EVIDENCE_SIGNATURES:
        raise AppealEvidenceValidationError(
            "Las evidencias de apelacion solo admiten archivos JPG o PNG.",
            status_code=422,
            error_code="INVALID_APPEAL_EVIDENCE_TYPE",
        )

    stream = file_storage.stream
    current_position = stream.tell()
    stream.seek(0, 2)
    file_size = stream.tell()
    stream.seek(0)

    if file_size > MAX_APPEAL_EVIDENCE_SIZE:
        stream.seek(current_position)
        raise AppealEvidenceValidationError(
            "Cada evidencia de apelacion puede pesar como maximo 5MB.",
            status_code=413,
            error_code="APPEAL_EVIDENCE_TOO_LARGE",
        )

    header = stream.read(16)
    stream.seek(0)
    if not any(header.startswith(signature) for signature in APPEAL_EVIDENCE_SIGNATURES[extension]):
        stream.seek(current_position)
        raise AppealEvidenceValidationError(
            "El contenido del archivo no coincide con una imagen JPG o PNG valida.",
            status_code=422,
            error_code="INVALID_APPEAL_EVIDENCE_TYPE",
        )

    filename = f"{uuid4().hex}.{extension}"
    relative_path = Path("uploads") / "apelaciones" / str(apelacion_id) / filename
    absolute_path = Path(upload_folder) / "apelaciones" / str(apelacion_id) / filename

    return {
        "file_storage": file_storage,
        "relative_path": str(relative_path).replace("\\", "/"),
        "absolute_path": absolute_path,
        "tipo_archivo": "IMAGEN",
    }
