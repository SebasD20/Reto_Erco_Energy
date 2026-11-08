
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

URL = "/calculate-concept"


@pytest.mark.integration
@pytest.mark.parametrize(
    "concepto, cantidad",
    [
        ("EA", "381.770"),
        ("EC", "594.970"),
        ("EE1", "381.770"),
        ("EE2", "213.20"),
    ]
)
def test_concepto_individual(concepto, cantidad):

    response = client.post(
        URL,
        json={
            "service_id": 2256,
            "year": 2023,
            "month": 9,
            "concept": concepto
        }
    )

    assert response.status_code == 200

    datos = response.json()

    assert datos["concept"] == concepto
    assert Decimal(
        datos["result"]["cantidad_kwh"]
    ) == Decimal(cantidad)

    assert "importe" in datos["result"]

    # La respuesta solo contiene el concepto solicitado
    assert "EA" not in datos
    assert "EC" not in datos
    assert "EE1" not in datos
    assert "EE2" not in datos


@pytest.mark.integration
@pytest.mark.parametrize(
    "service_id, year, month",
    [
        (999999, 2023, 9),
        (2256, 2024, 1),
    ]
)
def test_concepto_sin_datos(service_id, year, month):

    response = client.post(
        URL,
        json={
            "service_id": service_id,
            "year": year,
            "month": month,
            "concept": "EE1"
        }
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "concepto, month",
    [
        ("EE3", 9),
        ("EA", 15),
    ]
)
def test_concepto_parametros_invalidos(concepto, month):

    response = client.post(
        URL,
        json={
            "service_id": 2256,
            "year": 2023,
            "month": month,
            "concept": concepto
        }
    )

    assert response.status_code == 422
