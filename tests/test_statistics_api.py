from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

URL = "/client-statistics"


# Prueba 1: estadísticas de los tres servicios
@pytest.mark.integration
@pytest.mark.parametrize(
    "service_id, consumo, inyeccion, balance",
    [
        (2256, "381.770", "594.970", "-213.200"),
        (2478, "562.970", "727.880", "-164.910"),
        (3222, "29768.373", "344.862", "29423.511"),
    ]
)
def test_estadisticas_mensuales(
    service_id,
    consumo,
    inyeccion,
    balance
):
    response = client.get(
        f"{URL}/{service_id}",
        params={
            "year": 2023,
            "month": 9
        }
    )

    assert response.status_code == 200

    datos = response.json()

    assert datos["service_id"] == service_id
    assert datos["cantidad_mediciones"] == 720

    assert Decimal(
        datos["consumo_total_kwh"]
    ) == Decimal(consumo)

    assert Decimal(
        datos["inyeccion_total_kwh"]
    ) == Decimal(inyeccion)

    assert Decimal(
        datos["balance_kwh"]
    ) == Decimal(balance)

    # Comprobar el promedio de consumo
    promedio = Decimal(datos["consumo_promedio_kwh"])
    esperado = Decimal(consumo) / Decimal("720")

    assert abs(promedio - esperado) < Decimal("0.000001")


# Prueba 2: consulta sin filtros temporales
@pytest.mark.integration
def test_estadisticas_sin_periodo():
    response = client.get(f"{URL}/2256")

    assert response.status_code == 200

    datos = response.json()

    assert datos["service_id"] == 2256
    assert datos["year"] is None
    assert datos["month"] is None
    assert datos["cantidad_mediciones"] == 720


# Prueba 3: servicios o periodos inexistentes
@pytest.mark.integration
@pytest.mark.parametrize(
    "service_id, year, month",
    [
        (999999, 2023, 9),
        (2256, 2024, 1),
    ]
)
def test_estadisticas_no_encontradas(
    service_id,
    year,
    month
):
    response = client.get(
        f"{URL}/{service_id}",
        params={
            "year": year,
            "month": month
        }
    )

    assert response.status_code == 404


# Prueba 4: parámetros incorrectos
@pytest.mark.parametrize(
    "params",
    [
        {"year": 2023},
        {"month": 9},
        {"year": 2023, "month": 15},
    ]
)
def test_estadisticas_parametros_invalidos(params):
    response = client.get(
        f"{URL}/2256",
        params=params
    )

    assert response.status_code == 422
