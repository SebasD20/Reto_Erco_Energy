
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.schemas.invoice import (
    InvoiceRequest,
    InvoiceResponse,
    ConceptRequest,
    ConceptResponse,
)
from app.services.billing import calcular_factura


router = APIRouter(tags=["Facturación"])


# Proporciona una sesión de PostgreSQL
def get_db():
    with SessionLocal() as db:
        yield db


@router.post(
    "/calculate-invoice",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK
)
def calculate_invoice(
    request: InvoiceRequest,
    db: Session = Depends(get_db)
):
    """Calcula EA, EC, EE1 y EE2 para un servicio y mes."""

    try:
        resultado = calcular_factura(
            db=db,
            service_id=request.service_id,
            anio=request.year,
            mes=request.month
        )

    except ValueError as error:
        mensaje = str(error)

        # El servicio o periodo no tiene información
        if mensaje in (
            "El servicio no existe",
            "No existen mediciones para ese periodo"
        ):
            codigo = status.HTTP_404_NOT_FOUND

        # Los datos disponibles presentan inconsistencias
        else:
            codigo = status.HTTP_409_CONFLICT

        raise HTTPException(
            status_code=codigo,
            detail=mensaje
        ) from error

    # Subtotal de los cuatro conceptos
    subtotal = sum(
        (
            resultado[concepto]["importe"]
            for concepto in ("EA", "EC", "EE1", "EE2")
        ),
        Decimal("0")
    )

    return {
        "service_id": resultado["service_id"],
        "year": resultado["anio"],
        "month": resultado["mes"],
        "EA": resultado["EA"],
        "EC": resultado["EC"],
        "EE1": resultado["EE1"],
        "EE2": resultado["EE2"],
        "subtotal_neto": subtotal
    }


@router.post(
    "/calculate-concept",
    response_model=ConceptResponse,
    status_code=status.HTTP_200_OK
)
def calculate_concept(
    request: ConceptRequest,
    db: Session = Depends(get_db)
):
    """
    Devuelve un concepto de facturación para
    un servicio y periodo determinado.
    """

    try:
        resultado = calcular_factura(
            db=db,
            service_id=request.service_id,
            anio=request.year,
            mes=request.month
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

    # Seleccionar únicamente el concepto solicitado
    concepto = resultado[request.concept]

    return {
        "service_id": resultado["service_id"],
        "year": resultado["anio"],
        "month": resultado["mes"],
        "concept": request.concept,
        "result": concepto
    }
