
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Consumption, Record


def obtener_carga_sistema(
    db: Session,
    year: int | None = None,
    month: int | None = None,
    limit: int = 24,
    offset: int = 0,
) -> dict:
    """Agrupa el consumo de los servicios por fecha y hora."""

    # 1. Construir filtros de fecha
    filtros = []

    if year is not None and month is not None:
        inicio = datetime(year, month, 1)

        if month == 12:
            fin = datetime(year + 1, 1, 1)
        else:
            fin = datetime(year, month + 1, 1)

        filtros = [
            Record.record_timestamp >= inicio,
            Record.record_timestamp < fin,
        ]

    # 2. Contar las horas y validar mediciones
    resumen = db.execute(
        select(
            func.count(
                func.distinct(Record.record_timestamp)
            ).label("horas"),
            func.count(Record.id_record).label("mediciones"),
            func.count(Consumption.id_record).label("con_consumo"),
        )
        .select_from(Record)
        .outerjoin(
            Consumption,
            Record.id_record == Consumption.id_record
        )
        .where(*filtros)
    ).one()

    if resumen.mediciones == 0:
        raise ValueError("No existen mediciones para ese periodo")

    if resumen.mediciones != resumen.con_consumo:
        raise ValueError("Existen mediciones sin consumo")

    # 3. Sumar consumos por cada fecha y hora
    consulta = (
        select(
            Record.record_timestamp.label("fecha_hora"),
            func.sum(Consumption.value).label("consumo_total_kwh"),
            func.count(Record.id_service).label("cantidad_servicios"),
        )
        .select_from(Record)
        .join(
            Consumption,
            Record.id_record == Consumption.id_record
        )
        .where(*filtros)
        .group_by(Record.record_timestamp)
        .order_by(Record.record_timestamp)
        .limit(limit)
        .offset(offset)
    )

    # 4. Ejecutar la consulta
    filas = db.execute(consulta).all()

    # 5. Construir el resultado
    return {
        "year": year,
        "month": month,
        "limit": limit,
        "offset": offset,
        "total_horas": resumen.horas,
        "items": [
            {
                "fecha_hora": fila.fecha_hora,
                "consumo_total_kwh": fila.consumo_total_kwh,
                "cantidad_servicios": fila.cantidad_servicios,
            }
            for fila in filas
        ],
    }
 