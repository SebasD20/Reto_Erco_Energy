from decimal import Decimal

import pytest

from app.services.billing import calcular_ee1


@pytest.mark.parametrize(
    "consumo, inyeccion, cantidad, importe",
    [
        ("100", "60", "60", "-42000"),
        ("100", "100", "100", "-70000"),
        ("100", "150", "100", "-70000"),
        ("100", "0", "0", "0"),
        ("0", "150", "0", "0"),
    ]
)
def test_calcular_ee1(
    consumo,
    inyeccion,
    cantidad,
    importe
):
    resultado = calcular_ee1(
        consumo=Decimal(consumo),
        inyeccion=Decimal(inyeccion),
        cu=Decimal("700")
    )

    assert resultado["cantidad_kwh"] == Decimal(cantidad)
    assert resultado["importe"] == Decimal(importe)


@pytest.mark.parametrize(
    "consumo, inyeccion, cu",
    [
        ("-10", "50", "700"),
        ("100", "-5", "700"),
        ("100", "50", "-700"),
    ]
)
def test_ee1_rechaza_valores_negativos(
    consumo,
    inyeccion,
    cu
):
    with pytest.raises(ValueError):
        calcular_ee1(
            consumo=Decimal(consumo),
            inyeccion=Decimal(inyeccion),
            cu=Decimal(cu)
        )
