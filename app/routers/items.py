from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/items", tags=["items"])


class ItemIn(BaseModel):
    nombre: str = Field(..., examples=["Teclado"])
    precio: float = Field(..., gt=0, examples=[59.9])


class ItemOut(ItemIn):
    id: int


db: dict[int, ItemOut] = {}


@router.post("/", response_model=ItemOut, status_code=201, summary="Crear un item")
def crear_item(item: ItemIn):
    nuevo = ItemOut(id=len(db) + 1, **item.model_dump())
    db[nuevo.id] = nuevo
    return nuevo


@router.get("/{item_id}", response_model=ItemOut, summary="Obtener un item")
def obtener_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return db[item_id]