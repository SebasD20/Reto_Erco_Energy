from fastapi import FastAPI

from app.routers import items

from app.routers.billing import router as billing_router
from app.routers.statistics import router as statistics_router
from app.routers.system_load import router as system_load_router

app = FastAPI(
    title="Mi API",
    description="API con documentación Swagger.",
    version="1.0.0",
)


app.include_router(billing_router)
app.include_router(statistics_router)
app.include_router(system_load_router)
app.include_router(items.router)



@app.get("/", tags=["root"])
def root():
    return {"mensaje": "API funcionando"}