
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.services.billing import calcular_ee2


INICIO = datetime(2023, 9, 1)


def test_ee2_ejemplo_documento():
    # Diez horas con 15 kWh inyectados por hora
    mediciones = [
        (
            INICIO + timedelta(hours=hora),
            Decimal("15"),
            Decimal("100")
        )
        for hora in range(10)
    ]

    resultado = calcular_ee2(
        consumo_mensual=Decimal("100"),
        mediciones=mediciones
    )

    assert resultado["cantidad_kwh"] == Decimal("50")
    assert resultado["importe"] == Decimal("-5000")

    cantidades = [
        fila["cantidad_kwh"]
        for fila in resultado["detalle_horario"]
    ]

    assert cantidades == [
        Decimal("5"),
        Decimal("15"),
        Decimal("15"),
        Decimal("15")
    ]


def test_ee2_con_precios_horarios_diferentes():
    # Datos intencionalmente desordenados
    mediciones = [
        (INICIO + timedelta(hours=2), Decimal("4"), Decimal("300")),
        (INICIO, Decimal("6"), Decimal("100")),
        (INICIO + timedelta(hours=1), Decimal("7"), Decimal("200")),
    ]

    resultado = calcular_ee2(
        consumo_mensual=Decimal("10"),
        mediciones=mediciones
    )

    # Inyección total: 17 kWh
    # EE2: 7 kWh
    # Hora 2: 3 * 200 = 600
    # Hora 3: 4 * 300 = 1200
    assert resultado["cantidad_kwh"] == Decimal("7")
    assert resultado["importe"] == Decimal("-1800")

    assert len(resultado["detalle_horario"]) == 2


def test_ee2_sin_excedentes():
    mediciones = [
        (INICIO, Decimal("20"), Decimal("100")),
        (INICIO + timedelta(hours=1), Decimal("30"), Decimal("200")),
    ]

    resultado = calcular_ee2(
        consumo_mensual=Decimal("100"),
        mediciones=mediciones
    )

    assert resultado["cantidad_kwh"] == Decimal("0")
    assert resultado["importe"] == Decimal("0")
    assert resultado["detalle_horario"] == []


def test_ee2_sin_consumo():
    mediciones = [
        (INICIO, Decimal("5"), Decimal("100")),
        (INICIO + timedelta(hours=1), Decimal("3"), Decimal("200")),
    ]

    resultado = calcular_ee2(
        consumo_mensual=Decimal("0"),
        mediciones=mediciones
    )

    assert resultado["cantidad_kwh"] == Decimal("8")
    assert resultado["importe"] == Decimal("-1100")


def test_ee2_rechaza_precio_xm_faltante():
    mediciones = [
        (INICIO, Decimal("15"), None)
    ]

    with pytest.raises(ValueError):
        calcular_ee2(
            consumo_mensual=Decimal("10"),
            mediciones=mediciones
        )


def test_ee2_rechaza_inyeccion_negativa():
    mediciones = [
        (INICIO, Decimal("-5"), Decimal("100"))
    ]

    with pytest.raises(ValueError):
        calcular_ee2(
            consumo_mensual=Decimal("10"),
            mediciones=mediciones
        )


def test_ee2_rechaza_consumo_negativo():
    with pytest.raises(ValueError):
        calcular_ee2(
            consumo_mensual=Decimal("-10"),
            mediciones=[]
        )
