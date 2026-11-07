from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.orm import Session

#from app.models import Service, Record, Consumption, Injection
from app.models import (
    Service,
    Record,
    Consumption,
    Injection,
    XMDataHourlyPerAgent,
)

def calcular_ee1(
    consumo: Decimal,
    inyeccion: Decimal,
    cu: Decimal
) -> dict[str, Decimal]:
    """
    Calcula el concepto EE1.

    La cantidad corresponde al menor valor entre
    consumo e inyección. Se aplica CU negativo.
    """

    # Validar que los valores sean correctos
    if consumo < 0 or inyeccion < 0 or cu < 0:
        raise ValueError(
            "El consumo, la inyección y CU no pueden ser negativos"
        )

    # Determinar la energía correspondiente a EE1
    cantidad_ee1 = min(consumo, inyeccion)

    # Aplicar la tarifa con signo negativo
    tarifa_ee1 = -cu

    # Calcular el importe monetario
    importe_ee1 = (
        cantidad_ee1 * tarifa_ee1
        if cantidad_ee1 > 0
        else Decimal("0")
    )

    return {
        "cantidad_kwh": cantidad_ee1,
        "tarifa": tarifa_ee1,
        "importe": importe_ee1
    }


def calcular_ee2(
    consumo_mensual: Decimal,
    mediciones: list[tuple[datetime, Decimal, Decimal | None]]
) -> dict:
    """
    Calcula EE2 mediante la acumulación cronológica
    de energía inyectada y su valoración horaria XM.

    Cada medición contiene:
    (fecha_hora, inyeccion_kwh, precio_xm)
    """

    if consumo_mensual < 0:
        raise ValueError("El consumo no puede ser negativo")

    acumulado = Decimal("0")
    ee2_total = Decimal("0")
    valor_xm_total = Decimal("0")
    detalle_horario = []

    # Procesar las mediciones cronológicamente
    mediciones_ordenadas = sorted(
        mediciones,
        key=lambda fila: fila[0]
    )

    for fecha, inyeccion, precio_xm in mediciones_ordenadas:

        if inyeccion < 0:
            raise ValueError("La inyección no puede ser negativa")

        if precio_xm is None:
            raise ValueError(
                f"No existe precio XM para la hora {fecha}"
            )

        # Excedente acumulado antes de esta hora
        excedente_anterior = max(
            acumulado - consumo_mensual,
            Decimal("0")
        )

        # Actualizar la inyección acumulada
        acumulado += inyeccion

        # Excedente acumulado después de esta hora
        excedente_actual = max(
            acumulado - consumo_mensual,
            Decimal("0")
        )

        # EE2 generado exclusivamente en esta hora
        ee2_hora = excedente_actual - excedente_anterior

        if ee2_hora > 0:
            importe_hora = ee2_hora * precio_xm

            ee2_total += ee2_hora
            valor_xm_total += importe_hora

            detalle_horario.append({
                "fecha": fecha,
                "cantidad_kwh": ee2_hora,
                "precio_xm": precio_xm,
                "importe": -importe_hora
            })

    # Verificar que no se pierda energía
    excedente_esperado = max(
        acumulado - consumo_mensual,
        Decimal("0")
    )

    if ee2_total != excedente_esperado:
        raise ValueError("Inconsistencia en el cálculo EE2")

    return {
        "cantidad_kwh": ee2_total,
        "tarifa": None,
        "importe": -valor_xm_total,
        "detalle_horario": detalle_horario
    }


def calcular_factura(
    db: Session,
    service_id: int,
    anio: int,
    mes: int
) -> dict:

    # 1. Validar el mes solicitado
    if not 1 <= mes <= 12:
        raise ValueError("El mes debe estar entre 1 y 12")

    # 2. Establecer el periodo de facturación
    inicio = datetime(anio, mes, 1)

    if mes == 12:
        fin = datetime(anio + 1, 1, 1)
    else:
        fin = datetime(anio, mes + 1, 1)

    # 3. Buscar el servicio
    servicio = db.get(Service, service_id)

    if servicio is None:
        raise ValueError("El servicio no existe")

    # 4. Obtener la tarifa correspondiente
    tarifa = servicio.tariff

    if tarifa is None:
        raise ValueError("El servicio no tiene una tarifa asociada")

    # 5. Consultar los totales de energía
    consulta = (
        select(
            func.count(Record.id_record).label("mediciones"),
            func.count(Consumption.id_record).label("con_consumo"),
            func.count(Injection.id_record).label("con_inyeccion"),
            func.sum(Consumption.value).label("consumo"),
            func.sum(Injection.value).label("inyeccion")
        )
        .select_from(Record)
        .outerjoin(
            Consumption,
            Record.id_record == Consumption.id_record
        )
        .outerjoin(
            Injection,
            Record.id_record == Injection.id_record
        )
        .where(
            Record.id_service == service_id,
            Record.record_timestamp >= inicio,
            Record.record_timestamp < fin
        )
    )

    datos = db.execute(consulta).one()

    if datos.mediciones == 0:
        raise ValueError("No existen mediciones para ese periodo")

    if (
        datos.con_consumo != datos.mediciones
        or datos.con_inyeccion != datos.mediciones
    ):
        raise ValueError("Existen mediciones incompletas")

    # 6. Obtener los valores decimales
    consumo: Decimal = datos.consumo
    inyeccion: Decimal = datos.inyeccion

    # 7. Calcular los importes
    valor_ea = consumo * tarifa.CU
    valor_ec = inyeccion * tarifa.C

    # Calcular EE1 reutilizando la función independiente
    concepto_ee1 = calcular_ee1(
        consumo=consumo,
        inyeccion=inyeccion,
        cu=tarifa.CU
    )
    
    # 8. Consultar inyecciones y precios horarios de XM
    consulta_horaria = (
        select(
            Record.record_timestamp,
            Injection.value.label("inyeccion_kwh"),
            XMDataHourlyPerAgent.value.label("precio_xm")
        )
        .select_from(Record)
        .join(
            Injection,
            Record.id_record == Injection.id_record
        )
        .outerjoin(
            XMDataHourlyPerAgent,
            Record.record_timestamp
            == XMDataHourlyPerAgent.record_timestamp
        )
        .where(
            Record.id_service == service_id,
            Record.record_timestamp >= inicio,
            Record.record_timestamp < fin
        )
        .order_by(Record.record_timestamp)
    )

    # 9. Ejecutar la consulta
    filas = db.execute(consulta_horaria).all()

    # Comprobar que no faltan mediciones de inyección
    if len(filas) != datos.mediciones:
        raise ValueError(
            "Existen mediciones sin información de inyección"
        )

    # 10. Preparar los datos para calcular_ee2()
    mediciones = [
        (
            fila.record_timestamp,
            fila.inyeccion_kwh,
            fila.precio_xm
        )
        for fila in filas
    ]

    # 11. Calcular EE2 reutilizando nuestra función
    concepto_ee2 = calcular_ee2(
        consumo_mensual=consumo,
        mediciones=mediciones
    )

    # 12. Verificar la distribución de energía
    if (
        concepto_ee1["cantidad_kwh"]
        + concepto_ee2["cantidad_kwh"]
        != inyeccion
    ):
        raise ValueError(
            "La suma de EE1 y EE2 no coincide "
            "con la inyección mensual"
        )
    
    # 8. Devolver los resultados
    return {
        "service_id": service_id,
        "anio": anio,
        "mes": mes,
        "EA": {
            "cantidad_kwh": consumo,
            "tarifa": tarifa.CU,
            "importe": valor_ea
        },
        "EC": {
            "cantidad_kwh": inyeccion,
            "tarifa": tarifa.C,
            "importe": valor_ec
        },
        "EE1": concepto_ee1,
        "EE2": concepto_ee2
    }
