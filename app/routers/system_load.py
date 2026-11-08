
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.system_load import SystemLoadResponse
from app.services.system_load import obtener_carga_sistema


router = APIRouter(tags=["Carga energética"])


@router.get(
    "/system-load",
    response_model=SystemLoadResponse
)
def system_load(
    year: int | None = Query(default=None, ge=1, le=9998),
    month: int | None = Query(default=None, ge=1, le=12),
    limit: int = Query(default=24, ge=1, le=168),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):

    # Los filtros de año y mes deben venir juntos
    if (year is None) != (month is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Debes indicar año y mes juntos"
        )

    try:
        return obtener_carga_sistema(
            db=db,
            year=year,
            month=month,
            limit=limit,
            offset=offset
        )

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "No existen mediciones para ese periodo":
            codigo = status.HTTP_404_NOT_FOUND
        else:
            codigo = status.HTTP_409_CONFLICT

        raise HTTPException(
            status_code=codigo,
            detail=mensaje
        ) from error
