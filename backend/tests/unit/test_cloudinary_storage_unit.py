from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from app import create_app
from app.utils.cloudinary_storage import (
    CloudinaryStorageError,
    delete_media_from_cloudinary,
    upload_media_to_cloudinary,
)


pytestmark = pytest.mark.unit


def test_create_app_configura_cloudinary_en_extensions(monkeypatch):
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "demo-cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "123456789")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "secret-value")

    app = create_app()

    assert app.config["CLOUDINARY_ENABLED"] is True
    assert app.extensions["cloudinary_configured"] is True


def test_upload_media_to_cloudinary_falla_si_no_esta_configurado(app):
    archivo = FileStorage(
        stream=BytesIO(b"\x89PNG\r\n\x1a\narchivo-demo"),
        filename="demo.png",
        content_type="image/png",
    )

    with app.app_context():
        with pytest.raises(CloudinaryStorageError, match="Cloudinary no esta configurado"):
            upload_media_to_cloudinary(archivo, anuncio_id=10)


def test_upload_media_to_cloudinary_retorna_metadatos(monkeypatch):
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "demo-cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "123456789")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "secret-value")
    monkeypatch.setenv("CLOUDINARY_FOLDER", "hardware-ayacucho/anuncios")

    app = create_app()

    captured = {}

    def fake_upload(stream, **kwargs):
        captured["stream_position_before"] = stream.tell()
        captured["kwargs"] = kwargs
        return {
            "secure_url": "https://res.cloudinary.com/demo/image/upload/v1/demo.png",
            "public_id": "imagen-demo",
            "resource_type": "image",
            "format": "png",
            "bytes": 1024,
            "width": 800,
            "height": 600,
            "version": "1",
        }

    monkeypatch.setattr("cloudinary.uploader.upload", fake_upload)

    archivo = FileStorage(
        stream=BytesIO(b"\x89PNG\r\n\x1a\narchivo-demo"),
        filename="demo.png",
        content_type="image/png",
    )

    with app.app_context():
        resultado = upload_media_to_cloudinary(archivo, anuncio_id=42)

    assert resultado["tipo_media"] == "imagen"
    assert (
        resultado["ruta_relativa"]
        == "https://res.cloudinary.com/demo/image/upload/v1/demo.png"
    )
    assert resultado["public_id"] == "imagen-demo"
    assert captured["stream_position_before"] == 0
    assert captured["kwargs"]["asset_folder"] == "hardware-ayacucho/anuncios/42"
    assert captured["kwargs"]["resource_type"] == "image"


def test_upload_media_to_cloudinary_falla_si_respuesta_no_tiene_secure_url(monkeypatch):
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "demo-cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "123456789")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "secret-value")

    app = create_app()

    monkeypatch.setattr(
        "cloudinary.uploader.upload",
        lambda *_args, **_kwargs: {"public_id": "solo-public-id"},
    )

    archivo = FileStorage(
        stream=BytesIO(b"\x89PNG\r\n\x1a\narchivo-demo"),
        filename="demo.png",
        content_type="image/png",
    )

    with app.app_context():
        with pytest.raises(CloudinaryStorageError, match="Cloudinary no devolvio los metadatos"):
            upload_media_to_cloudinary(archivo, anuncio_id=99)


def test_delete_media_from_cloudinary_retorna_respuesta_sdk(monkeypatch):
    monkeypatch.setenv("FLASK_APP_SECRET", "x" * 48)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 48)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "demo-cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "123456789")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "secret-value")

    app = create_app()

    captured = {}

    def fake_destroy(public_id, **kwargs):
        captured["public_id"] = public_id
        captured["kwargs"] = kwargs
        return {"result": "ok"}

    monkeypatch.setattr("cloudinary.uploader.destroy", fake_destroy)

    with app.app_context():
        resultado = delete_media_from_cloudinary("media-demo", "image")

    assert resultado == {"result": "ok"}
    assert captured["public_id"] == "media-demo"
    assert captured["kwargs"]["resource_type"] == "image"
    assert captured["kwargs"]["invalidate"] is True
