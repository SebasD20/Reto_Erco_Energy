"""Consultas agregadas para estadísticas energéticas por servicio."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Consumption, Injection, Record, Service


def obtener_estadisticas_servicio(
    db: Session,
    service_id: int,
    year: int | None = None,
    month: int | None = None,
) -> dict:
    """Devuelve estadísticas de consumo e inyección del servicio solicitado.

    Si year y month están presentes, limita las mediciones a ese mes.
    Ambos filtros juntos o ninguno: el router valida la petición HTTP.
    """
    servicio = db.get(Service, service_id)
    if servicio is None:
        raise ValueError("El servicio no existe")

    consulta = (
        select(
            func.count(Record.id_record).label("mediciones"),
            func.count(Consumption.id_record).label("con_consumo"),
            func.count(Injection.id_record).label("con_inyeccion"),
            func.sum(Consumption.value).label("consumo_total"),
            func.sum(Injection.value).label("inyeccion_total"),
            func.avg(Consumption.value).label("consumo_promedio"),
            func.avg(Injection.value).label("inyeccion_promedio"),
            func.max(Consumption.value).label("consumo_maximo"),
            func.max(Injection.value).label("inyeccion_maxima"),
        )
        .select_from(Record)
        .outerjoin(Consumption, Record.id_record == Consumption.id_record)
        .outerjoin(Injection, Record.id_record == Injection.id_record)
        .where(Record.id_service == service_id)
    )

    if year is not None and month is not None:
        inicio = datetime(year, month, 1)
        if month == 12:
            fin = datetime(year + 1, 1, 1)
        else:
            fin = datetime(year, month + 1, 1)
        consulta = consulta.where(
            Record.record_timestamp >= inicio,
            Record.record_timestamp < fin,
        )

    datos = db.execute(consulta).one()
    if datos.mediciones == 0:
        raise ValueError("No existen mediciones para ese periodo")
    if (
        datos.con_consumo != datos.mediciones
        or datos.con_inyeccion != datos.mediciones
    ):
        raise ValueError("Existen mediciones incompletas")

    return {
        "service_id": service_id,
        "year": year,
        "month": month,
        "cantidad_mediciones": datos.mediciones,
        "consumo_total_kwh": datos.consumo_total,
        "inyeccion_total_kwh": datos.inyeccion_total,
        "balance_kwh": datos.consumo_total - datos.inyeccion_total,
        "consumo_promedio_kwh": datos.consumo_promedio,
        "inyeccion_promedio_kwh": datos.inyeccion_promedio,
        "consumo_maximo_kwh": datos.consumo_maximo,
        "inyeccion_maxima_kwh": datos.inyeccion_maxima,
    }
