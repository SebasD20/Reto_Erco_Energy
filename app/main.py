from fastapi import FastAPI

from app.routers import items

app = FastAPI(
    title="Mi API",
    description="API con documentación Swagger.",
    version="1.0.0",
)

app.include_router(items.router)


@app.get("/", tags=["root"])
def root():
    return {"mensaje": "API funcionando"}