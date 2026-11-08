
from decimal import Decimal, ROUND_HALF_UP

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

URL = "/calculate-invoice"


@pytest.mark.integration
@pytest.mark.parametrize(
    "service_id, cantidad_ee2, importe_ee2",
    [
        (2256, "213.20", "-225869.29"),
        (2478, "164.91", "-174350.73"),
        (3222, "0", "0.00"),
    ]
)
def test_calcular_factura(
    service_id,
    cantidad_ee2,
    importe_ee2
):
    # Enviar una solicitud HTTP
    response = client.post(
        URL,
        json={
            "service_id": service_id,
            "year": 2023,
            "month": 9
        }
    )

    # Verificar el código de respuesta
    assert response.status_code == 200

    # Convertir el JSON a un diccionario Python
    datos = response.json()

    # Verificar los conceptos
    for concepto in ("EA", "EC", "EE1", "EE2"):
        assert concepto in datos

    # Comprobar la cantidad de EE2
    assert Decimal(
        datos["EE2"]["cantidad_kwh"]
    ) == Decimal(cantidad_ee2)

    # Comprobar el importe de EE2
    importe = Decimal(
        datos["EE2"]["importe"]
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    assert importe == Decimal(importe_ee2)

    # Comprobar conservación de energía
    ee1 = Decimal(datos["EE1"]["cantidad_kwh"])
    ee2 = Decimal(datos["EE2"]["cantidad_kwh"])
    inyeccion = Decimal(datos["EC"]["cantidad_kwh"])

    assert ee1 + ee2 == inyeccion


@pytest.mark.integration
@pytest.mark.parametrize(
    "service_id, year, month",
    [
        (999999, 2023, 9),
        (2256, 2024, 1),
    ]
)
def test_factura_no_encontrada(
    service_id,
    year,
    month
):
    response = client.post(
        URL,
        json={
            "service_id": service_id,
            "year": year,
            "month": month
        }
    )

    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.parametrize(
    "service_id, year, month",
    [
        (2256, 2023, 15),
        (0, 2023, 9),
    ]
)
def test_parametros_invalidos(
    service_id,
    year,
    month
):
    response = client.post(
        URL,
        json={
            "service_id": service_id,
            "year": year,
            "month": month
        }
    )

    assert response.status_code == 422
