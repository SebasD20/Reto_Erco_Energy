# Contrato HTTP — API Reto Erco

Base URL local: `http://127.0.0.1:8000`. Documentación interactiva: `/docs`. Las respuestas decimales usan **cadenas JSON** para preservar la precisión monetaria.

## POST `/calculate-invoice`

Body requerido:

```json
{"service_id":2256,"year":2023,"month":9}
```

Validaciones: `service_id > 0`, `year` entre 1 y 9998, `month` entre 1 y 12. Respuesta HTTP 200:

```json
{
  "service_id":2256,
  "year":2023,
  "month":9,
  "EA":{"cantidad_kwh":"381.770000","tarifa":"770.73000000","importe":"294241.592100000000"},
  "EC":{"cantidad_kwh":"594.970000","tarifa":"23.94000000","importe":"14243.581800000000"},
  "EE1":{"cantidad_kwh":"381.770000","tarifa":"-770.73000000","importe":"-294241.592100000000"},
  "EE2":{"cantidad_kwh":"213.200000","tarifa":null,"importe":"-225869.2938705220240000"},
  "subtotal_neto":"-211625.7120705220240000"
}
```

Los ceros finales pueden variar según el contexto decimal. Importes según el supuesto de EE2 como crédito negativo; subtotal sin impuestos ni otros ajustes.

## POST `/calculate-concept`

Body:

```json
{"service_id":2256,"year":2023,"month":9,"concept":"EE2"}
```

`concept` admite únicamente `EA`, `EC`, `EE1`, `EE2`. Respuesta 200:

```json
{
  "service_id":2256,"year":2023,"month":9,"concept":"EE2",
  "result":{"cantidad_kwh":"213.200000","tarifa":null,"importe":"-225869.2938705220240000"}
}
```

## GET `/client-statistics/{service_id}`

Opcionalmente filtrar mediante `year` y `month`; deben suministrarse ambos o ninguno.

```http
GET /client-statistics/2256?year=2023&month=9
```

Respuesta 200 de referencia: `cantidad_mediciones = 720`, `consumo_total_kwh = 381.770000`, `inyeccion_total_kwh = 594.970000`, `balance_kwh = -213.200000`. Adicionalmente retorna `consumo_promedio_kwh`, `inyeccion_promedio_kwh`, `consumo_maximo_kwh` e `inyeccion_maxima_kwh`. Sin filtros se consulta todo el historial disponible para el servicio.

## GET `/system-load`

Acepta filtros opcionales por `year` y `month`, y paginación con `limit` y `offset`:

- `year`: 1–9998, opcional (junto con `month`).
- `month`: 1–12, opcional (junto con `year`).
- `limit`: 1–168, valor por defecto 24.
- `offset`: entero no negativo, valor por defecto 0.

```http
GET /system-load?year=2023&month=9&limit=2&offset=0
```

```json
{
  "year":2023,"month":9,"limit":2,"offset":0,"total_horas":720,
  "items":[
    {"fecha_hora":"2023-09-01T00:00:00","consumo_total_kwh":"55.725000","cantidad_servicios":3},
    {"fecha_hora":"2023-09-01T01:00:00","consumo_total_kwh":"63.960000","cantidad_servicios":3}
  ]
}
```

Para una segunda página utilizar `offset=2` (horas 02:00 y 03:00). Cada fila es la suma de consumo de todos los servicios en la misma hora; `total_horas` cuenta las horas disponibles, no el número de registros originales.

## Errores HTTP

| Código | Significado | Ejemplos |
|---|---|---|
| 200 | Solicitud procesada | Cálculo o consulta correcta |
| 404 | No se encontró información | Servicio inexistente; periodo sin mediciones |
| 409 | Datos del dominio inconsistentes | Mediciones incompletas; falta una tarifa; falta precio XM |
| 422 | Validación de parámetros | Mes 15; ID no válido; concepto distinto de EA/EC/EE1/EE2 |

Errores típicos: `{"detail":"El servicio no existe"}` o estructura de errores de validación de FastAPI/Pydantic. Los códigos 404 y 409 reflejan la implementación actual basada en `ValueError`.
