
from decimal import Decimal, ROUND_HALF_UP

import pytest

from app.db import SessionLocal
from app.services.billing import calcular_factura


@pytest.mark.integration
@pytest.mark.parametrize(
    "service_id, cantidad, importe, horas",
    [
        (2256, "213.20", "-225869.29", 116),
        (2478, "164.91", "-174350.73", 88),
        (3222, "0", "0.00", 0),
    ]
)
def test_facturacion_con_postgresql(
    service_id,
    cantidad,
    importe,
    horas
):
    with SessionLocal() as db:
        resultado = calcular_factura(
            db=db,
            service_id=service_id,
            anio=2023,
            mes=9
        )

    ee1 = resultado["EE1"]
    ee2 = resultado["EE2"]
    ec = resultado["EC"]

    # Verificar cantidad energética de EE2
    assert ee2["cantidad_kwh"] == Decimal(cantidad)

    # Verificar importe con dos decimales
    importe_calculado = ee2["importe"].quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    assert importe_calculado == Decimal(importe)

    # Verificar número de horas con EE2
    assert len(ee2["detalle_horario"]) == horas

    # Toda la inyección debe distribuirse entre EE1 y EE2
    assert (
        ee1["cantidad_kwh"] + ee2["cantidad_kwh"]
        == ec["cantidad_kwh"]
    )

    # El detalle horario debe sumar el total calculado
    assert sum(
        (fila["cantidad_kwh"] for fila in ee2["detalle_horario"]),
        Decimal("0")
    ) == ee2["cantidad_kwh"]
