from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename


REPORT_EVIDENCE_SIGNATURES = {
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    "png": (b"\x89PNG\r\n\x1a\n",),
}

MAX_REPORT_EVIDENCES = 3
MAX_REPORT_EVIDENCE_SIZE = 5 * 1024 * 1024


class ReportEvidenceValidationError(Exception):
    def __init__(self, message, status_code=422, error_code="INVALID_REPORT_EVIDENCE"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


def validate_report_evidences(files, upload_folder, reporte_id):
    files = [file_storage for file_storage in files if file_storage and file_storage.filename]
    if not files:
        return []

    if len(files) > MAX_REPORT_EVIDENCES:
        raise ReportEvidenceValidationError(
            f"Solo se permiten hasta {MAX_REPORT_EVIDENCES} evidencias por reporte.",
            status_code=422,
            error_code="TOO_MANY_REPORT_EVIDENCES",
        )

    validated = []
    for file_storage in files:
        validated.append(_validate_single_report_evidence(file_storage, upload_folder, reporte_id))
    return validated


def persist_report_evidences(validated_files):
    for item in validated_files:
        item["absolute_path"].parent.mkdir(parents=True, exist_ok=True)
        item["file_storage"].stream.seek(0)
        item["file_storage"].save(item["absolute_path"])


def delete_report_evidences(validated_files):
    for item in validated_files:
        try:
            item["absolute_path"].unlink(missing_ok=True)
        except OSError:
            pass


def _validate_single_report_evidence(file_storage, upload_folder, reporte_id):
    original_name = secure_filename(file_storage.filename)
    extension = Path(original_name).suffix.lower().lstrip(".")
    if extension not in REPORT_EVIDENCE_SIGNATURES:
        raise ReportEvidenceValidationError(
            "Las evidencias solo admiten archivos JPG o PNG.",
            status_code=422,
            error_code="INVALID_REPORT_EVIDENCE_TYPE",
        )

    stream = file_storage.stream
    current_position = stream.tell()
    stream.seek(0, 2)
    file_size = stream.tell()
    stream.seek(0)

    if file_size > MAX_REPORT_EVIDENCE_SIZE:
        stream.seek(current_position)
        raise ReportEvidenceValidationError(
            "Cada evidencia puede pesar como maximo 5MB.",
            status_code=413,
            error_code="REPORT_EVIDENCE_TOO_LARGE",
        )

    header = stream.read(16)
    stream.seek(0)
    if not any(header.startswith(signature) for signature in REPORT_EVIDENCE_SIGNATURES[extension]):
        stream.seek(current_position)
        raise ReportEvidenceValidationError(
            "El contenido del archivo no coincide con una imagen JPG o PNG valida.",
            status_code=422,
            error_code="INVALID_REPORT_EVIDENCE_TYPE",
        )

    filename = f"{uuid4().hex}.{extension}"
    relative_path = Path("uploads") / "reportes" / str(reporte_id) / filename
    absolute_path = Path(upload_folder) / "reportes" / str(reporte_id) / filename

    return {
        "file_storage": file_storage,
        "relative_path": str(relative_path).replace("\\", "/"),
        "absolute_path": absolute_path,
        "tipo_archivo": "IMAGEN",
    }
