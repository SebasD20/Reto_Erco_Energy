from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.statistics import ClientStatisticsResponse
from app.services.statistics import obtener_estadisticas_servicio


router = APIRouter(tags=["Estadísticas"])


@router.get(
    "/client-statistics/{service_id}",
    response_model=ClientStatisticsResponse
)
def client_statistics(
    service_id: int,
    year: int | None = Query(default=None, ge=1, le=9998),
    month: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db)
):

    # Año y mes deben suministrarse juntos o ninguno
    if (year is None) != (month is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Debes indicar año y mes juntos"
        )

    try:
        return obtener_estadisticas_servicio(
            db=db,
            service_id=service_id,
            year=year,
            month=month
        )

    except ValueError as error:
        mensaje = str(error)

        if mensaje in (
            "El servicio no existe",
            "No existen mediciones para ese periodo"
        ):
            codigo = status.HTTP_404_NOT_FOUND
        else:
            codigo = status.HTTP_409_CONFLICT

        raise HTTPException(
            status_code=codigo,
            detail=mensaje
        ) from error
