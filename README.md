# Reto Erco — API de facturación y análisis energético

Prueba técnica Backend Middle (Python / PostgreSQL). La aplicación implementa cálculo de cuatro conceptos energéticos, consulta de estadísticas por servicio y carga energética horaria del sistema.

## Stack

- Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2, PostgreSQL, Alembic y pytest.
- Consultas y operaciones monetarias con `NUMERIC` en PostgreSQL y `Decimal` en Python.
- Documentación interactiva OpenAPI en `/docs`.

## Estructura

```text
app/
  main.py                # instancia de FastAPI y registro de routers
  db.py                  # motor, SessionLocal y dependencia get_db
  core/config.py         # configuración mediante DATABASE_URL en .env
  models/                # modelos SQLAlchemy
  routers/               # endpoints HTTP
  schemas/               # modelos Pydantic de entrada y respuesta
  services/              # consultas y reglas de negocio
  load_csv.py            # importación de datos originales
alembic/versions/        # migraciones de estructura
csv o data/              # archivos CSV suministrados
scripts o db/schema.sql  # esquema de referencia SQL
scripts o db/validacion.sql # consultas de verificación
scripts o tests/         # batería pytest
```

## Requisitos

- Python 3.13 (se ha probado localmente con Python 3.13).
- PostgreSQL activo, base de datos creada y credenciales con acceso.
- Git para la entrega. No es necesario Docker para ejecutar localmente.

## Instalación (Windows / PowerShell)

1. Clonar el repositorio y abrir la carpeta raíz `Reto Erco` en VS Code.
2. Crear el entorno e instalar las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, habilitar la política solo para la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

3. Copiar `.env.example` a `.env` y completar la conexión REAL. Nunca compartir ni subir `.env`:

```powershell
Copy-Item .env.example .env
```

La variable requerida es `DATABASE_URL` (ver `.env.example`). La contraseña se debe reemplazar en el entorno local; los caracteres especiales deben codificarse para URLs cuando aplique.

4. Crear la base de datos en PostgreSQL si aún no existe. Ejecutar las migraciones **del repositorio**:

```powershell
alembic upgrade head
alembic current
```

5. Si la BD está vacía, cargar los CSV suministrados, ubicados en `data/`:

```powershell
python -m app.load_csv
```

**No ejecutar la carga por segunda vez sobre datos existentes**: el cargador actual utiliza COPY y puede provocar conflictos de claves duplicadas. En una instalación nueva, ejecutar una sola vez tras las migraciones. No ejecutar `db/schema.sql` y Alembic sobre la misma BD: son rutas alternativas para reproducir la estructura; Alembic es la ruta utilizada por la aplicación.

6. Levantar la API:

```powershell
python -m uvicorn app.main:app --reload --reload-dir app
```

Abrir [Swagger](http://127.0.0.1:8000/docs), o [OpenAPI JSON](http://127.0.0.1:8000/openapi.json).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/calculate-invoice` | Calcula EA, EC, EE1 y EE2 y subtotal neto mensual |
| POST | `/calculate-concept` | Devuelve solo uno de los cuatro conceptos |
| GET | `/client-statistics/{service_id}` | Totales, promedios, máximos y balance por servicio |
| GET | `/system-load` | Suma el consumo de todos los servicios por hora, paginado |

Ejemplo de factura:

```http
POST /calculate-invoice
Content-Type: application/json
```

```json
{"service_id": 2256, "year": 2023, "month": 9}
```

Ejemplo de carga horaria:

```http
GET /system-load?year=2023&month=9&limit=24&offset=0
```

Consultar [docs/API.md](docs/API.md) para los parámetros, respuestas, ejemplos y errores.

## Reglas de facturación

Para un servicio y mes: `C_m = SUM(consumption.value)` e `I_m = SUM(injection.value)`; se selecciona la tarifa aplicable por mercado, voltaje y CDI cuando corresponde.

- **EA** = `C_m × CU` (cargo).
- **EC** = `I_m × tarifa.C` (cargo de comercialización).
- **EE1** = `min(C_m, I_m) × (−CU)` (crédito).
- **EE2**: si `I_m > C_m`, los excedentes de inyección se distribuyen cronológicamente por hora, a partir del umbral de `C_m`, y cada fracción se multiplica por el precio XM de esa hora. El importe se registra como crédito negativo por la interpretación adoptada.

El subtotal es la suma de los cuatro importes; **no representa necesariamente el importe final de pago** porque el ejercicio no define impuestos, arrastres de saldo ni otros cargos. Véase [docs/DECISIONES_TECNICAS.md](docs/DECISIONES_TECNICAS.md).

## Pruebas

Requieren pytest; las de integración requieren PostgreSQL con los CSV originales.

```powershell
python -m pytest tests/ -v
python -m pytest -m "not integration" -v
```

Si el archivo `tests/test_system_load_api.py` ya está añadido, hay 12 casos adicionales para el cuarto endpoint. El resultado de la ejecución completa debe validarse en el entorno de entrega; no se debe afirmar que pasó sin ejecutar los comandos allí.

## Datos e integridad

El conjunto de muestra contiene 3 servicios; 2.160 mediciones; 2.160 consumos; 2.160 inyecciones; 105 tarifas y 720 precios XM (7.308 filas en las seis tablas de datos). Ventana de referencia: septiembre de 2023, 720 horas. El CSV se trata como fuente de prueba, no como datos de producción.

Se aplican restricciones de unicidad y no negatividad en la base de datos, y validaciones de integridad en los servicios antes de calcular conceptos. La fecha `record_timestamp` se maneja sin zona horaria, según el material entregado.

## Esquema y mantenimiento

- Migraciones: `alembic/versions/` son la referencia operativa del esquema.
- Esquema SQL de referencia para entrega: `db/schema.sql` (no aplicar a una BD ya migrada).
- Verificación no destructiva: `db/validacion.sql`.
- Supuestos, decisiones, riesgos y mejoras: `docs/DECISIONES_TECNICAS.md`.
- API HTTP: `docs/API.md`. 

## Consideraciones de seguridad

Configurar credenciales únicamente en `.env`; el archivo debe estar ignorado por Git. Evitar publicar `.venv`, `.git`, `__pycache__`, `.pytest_cache`. La aplicación es una prueba local y **no incluye autenticación, despliegue productivo ni gestión de secretos**.
