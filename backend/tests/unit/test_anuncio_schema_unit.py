from decimal import Decimal

import pytest
from marshmallow import ValidationError

from app.schemas.anuncio_schema import _normalizar_taxonomia, _validar_decimal_positivo


pytestmark = pytest.mark.unit


def test_normalizar_taxonomia_convierte_a_mayusculas_y_guiones_bajos():
    assert _normalizar_taxonomia("placa madre-am4") == "PLACA_MADRE_AM4"


def test_validar_decimal_positivo_acepta_valor_valido():
    assert _validar_decimal_positivo(Decimal("10.50"), "precio_min") is None


def test_validar_decimal_positivo_rechaza_texto_no_numerico():
    with pytest.raises(ValidationError, match="precio_min debe ser numerico."):
        _validar_decimal_positivo("abc", "precio_min")


def test_validar_decimal_positivo_rechaza_cero_o_negativo():
    with pytest.raises(ValidationError, match="precio_max debe ser mayor que 0."):
        _validar_decimal_positivo("0", "precio_max")
