from pathlib import Path
from types import SimpleNamespace

import pytest

from app.services.anuncio_service import (
    _absolute_media_path,
    _build_applied_filters,
    _diversify_feed_records,
    _escape_like,
    _expand_search_terms,
    _json_merge_patch,
    _normalizar_reactivaciones_count,
    _reindexar_imagenes,
    _sanitize_contact_title,
    _same_seller,
    _validar_estado_comprador_contacto,
    _validar_estado_edicion,
    _validar_estado_para_reactivar,
    _validar_estado_para_vendido,
)


pytestmark = pytest.mark.unit


def test_escape_like_escapa_porcentaje_guion_bajo_y_backslash():
    assert _escape_like(r"AM%4_\socket") == r"AM\%4\_\\socket"


def test_expand_search_terms_agrega_alias_de_busqueda():
    terms = set(_expand_search_terms("motherboard"))
    assert "motherboard" in terms
    assert "placa madre" in terms
    assert "placa_madre" in terms


def test_sanitize_contact_title_elimina_comillas_y_control_chars():
    assert _sanitize_contact_title('  "Ryzen"\n5700X\x7f  ') == "Ryzen5700X"


def test_build_applied_filters_serializa_specs_y_decimales():
    applied = _build_applied_filters({
        "order_by": "reciente",
        "categoria": "COMPONENTES",
        "subcategoria": "PROCESADOR",
        "condicion": None,
        "q": None,
        "precio_min": 400,
        "precio_max": "900",
        "specs": {"socket": "AM4"},
    })

    assert applied == {
        "order_by": "reciente",
        "categoria": "COMPONENTES",
        "subcategoria": "PROCESADOR",
        "precio_min": "400",
        "precio_max": "900",
        "specs": {"socket": "AM4"},
    }


def test_validar_estado_edicion_rechaza_anuncio_bloqueado():
    anuncio = SimpleNamespace(estado="BLOQUEADO")

    assert _validar_estado_edicion(anuncio) == {
        "success": False,
        "data": {},
        "error": "FORBIDDEN",
        "message": "El anuncio se encuentra bloqueado.",
    }


def test_validar_estado_para_vendido_rechaza_inactivo():
    anuncio = SimpleNamespace(estado="INACTIVO")

    assert _validar_estado_para_vendido(anuncio) == {
        "success": False,
        "data": {},
        "error": "CONFLICT",
        "message": "El anuncio inactivo no puede marcarse como vendido.",
    }


def test_validar_estado_para_reactivar_rechaza_anuncio_activo():
    anuncio = SimpleNamespace(estado="ACTIVO")

    assert _validar_estado_para_reactivar(anuncio) == {
        "success": False,
        "data": {},
        "error": "CONFLICT",
        "message": "El anuncio ya se encuentra activo.",
    }


def test_validar_estado_comprador_contacto_rechaza_tienda_en_revision():
    usuario = SimpleNamespace(
        estado="ACTIVO",
        rol="TIENDA_VERIFICADA",
        tienda=SimpleNamespace(estado="EN_REVISION"),
    )

    assert _validar_estado_comprador_contacto(usuario) == {
        "success": False,
        "data": {},
        "error": "FORBIDDEN",
        "message": "La cuenta debe estar activa para contactar anuncios.",
    }


def test_normalizar_reactivaciones_count_convierte_none_a_cero():
    anuncio = SimpleNamespace(reactivaciones_count=None)
    assert _normalizar_reactivaciones_count(anuncio) == 0


def test_json_merge_patch_conserva_no_enviados_y_elimina_nulls():
    current_value = {
        "socket": "AM4",
        "extras": {"rgb": True, "wifi": True},
        "marca": "MSI",
    }
    patch_value = {
        "extras": {"rgb": None, "bluetooth": True},
        "marca": None,
    }

    assert _json_merge_patch(current_value, patch_value) == {
        "socket": "AM4",
        "extras": {"wifi": True, "bluetooth": True},
    }


def test_reindexar_imagenes_actualiza_orden_y_principal():
    imagenes = [
        SimpleNamespace(orden=8, es_principal=False),
        SimpleNamespace(orden=4, es_principal=True),
        SimpleNamespace(orden=2, es_principal=False),
    ]

    _reindexar_imagenes(imagenes)

    assert [(img.orden, img.es_principal) for img in imagenes] == [
        (0, True),
        (1, False),
        (2, False),
    ]


def test_absolute_media_path_remueve_prefijo_uploads():
    result = _absolute_media_path("C:/tmp/base", "uploads/anuncios/1/main.jpg")
    assert result == Path("C:/tmp/base") / "anuncios" / "1" / "main.jpg"


def test_same_seller_y_diversify_feed_records_intercalan_vendedores():
    records = [
        SimpleNamespace(id=1, vendedor_id=10, vendedor_nombre="A"),
        SimpleNamespace(id=2, vendedor_id=10, vendedor_nombre="A"),
        SimpleNamespace(id=3, vendedor_id=20, vendedor_nombre="B"),
        SimpleNamespace(id=4, vendedor_id=20, vendedor_nombre="B"),
    ]

    diversified = _diversify_feed_records(records)

    assert _same_seller(records[0], records[1]) is True
    assert _same_seller(records[0], records[2]) is False
    assert [item.id for item in diversified] == [1, 3, 2, 4]
