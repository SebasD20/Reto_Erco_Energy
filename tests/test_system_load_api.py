from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
URL = "/system-load"

@pytest.mark.integration
@pytest.mark.parametrize("offset, valores", [
    (0, ["55.725", "63.960"]),
    (2, ["62.751", "58.887"]),
])
def test_paginacion(offset, valores):
    response = client.get(URL, params={"year": 2023, "month": 9, "limit": 2, "offset": offset})
    assert response.status_code == 200
    datos = response.json()
    assert datos["total_horas"] == 720
    assert datos["limit"] == 2
    assert datos["offset"] == offset
    assert len(datos["items"]) == 2
    for fila, esperado in zip(datos["items"], valores):
        assert Decimal(fila["consumo_total_kwh"]) == Decimal(esperado)
        assert fila["cantidad_servicios"] == 3

@pytest.mark.integration
def test_consumo_total_mensual():
    horas = []
    consumo = Decimal("0")
    for offset in range(0, 720, 168):
        response = client.get(URL, params={"year": 2023, "month": 9, "limit": 168, "offset": offset})
        assert response.status_code == 200
        datos = response.json()
        assert datos["total_horas"] == 720
        for fila in datos["items"]:
            horas.append(fila["fecha_hora"])
            consumo += Decimal(fila["consumo_total_kwh"])
    assert len(horas) == 720
    assert len(set(horas)) == 720
    assert horas == sorted(horas)
    assert consumo == Decimal("30713.113")

@pytest.mark.integration
def test_sin_periodo():
    response = client.get(URL)
    assert response.status_code == 200
    datos = response.json()
    assert datos["year"] is None and datos["month"] is None
    assert datos["limit"] == 24
    assert datos["total_horas"] == 720
    assert len(datos["items"]) == 24

@pytest.mark.integration
def test_periodo_inexistente():
    response = client.get(URL, params={"year": 2024, "month": 1})
    assert response.status_code == 404

@pytest.mark.parametrize("params", [
    {"year": 2023}, {"month": 9}, {"year": 2023, "month": 15},
    {"limit": 0}, {"limit": 169}, {"offset": -1},
])
def test_parametros_invalidos(params):
    response = client.get(URL, params=params)
    assert response.status_code == 422

@pytest.mark.integration
def test_offset_fuera_de_rango():
    response = client.get(URL, params={"year": 2023, "month": 9, "limit": 2, "offset": 1000})
    assert response.status_code == 200
    datos = response.json()
    assert datos["total_horas"] == 720
    assert datos["items"] == []
