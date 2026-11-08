# Decisiones técnicas, supuestos y mejoras

## 1. Diseño de base de datos

Se preservaron las seis entidades del material original: `services`, `tariffs`, `records`, `consumption`, `injection` y `xm_data_hourly_per_agent`.

**Selección tarifaria.** `id_market` no es único en `tariffs`: existen varias tarifas por mercado según nivel de voltaje y CDI. Por ello se añadió `id_tariff` como clave primaria técnica. El servicio selecciona una tarifa mediante `id_market` + `voltage_level` y, si el voltaje es 1, también `cdi`. En la implementación actual, niveles 2/3 buscan CDI nulo en la fila de tarifa: esto funciona con los datos entregados, pero es más restrictivo que «CDI no importa» del enunciado. En una mejora futura debe ignorarse explícitamente CDI en esos niveles **junto con** un índice único por `(id_market,voltage_level)` para niveles 2/3; no modificar solo el JOIN.

**Integridad.** Cada medición está identificada por `id_record` y vinculada al servicio y a la hora. `consumption` y `injection` son uno a uno con `records` mediante PK/FK. Se establecen restricciones de no negatividad y unicidad de `(id_service,record_timestamp)`; `record_timestamp` relaciona los registros con el precio XM.

**Tipos.** Energía y tarifas se almacenan con `NUMERIC`, para evitar errores del tipo `0.1 + 0.2` asociados a representación de coma flotante binaria; en Python se utilizan objetos `Decimal`.

## 2. Interpretación de facturación

El enunciado es ambiguo sobre el signo monetario de EE2: describe «consumo menos inyección», pero su ejemplo calcula `150-100=50` kWh de EE2 y asigna precios XM a los excedentes posteriores al cruce del umbral. Se distinguió entre **cantidad de energía positiva** y **efecto contable negativo** (crédito). Esta decisión se aplicó de forma consistente y se documenta, pero no constituye confirmación externa del negocio.

- EA: suma mensual de consumo por CU, importe positivo.
- EC: suma mensual de inyección por componente `C`, importe positivo.
- EE1: mínimo entre consumo e inyección por `-CU`.
- EE2: excedente `max(inyección_total−consumo_total,0)` distribuido por hora según acumulación cronológica; cada fracción se multiplica por precio XM de su hora, con importe negativo.

Se verifica la invariancia energética: `EE1_kWh + EE2_kWh = inyección_total_kWh`. El subtotal es suma de los importes, **no factura final a pagar**: el enunciado no contempla impuestos, saldos trasladables ni más componentes.

No se redondean los importes horarios antes de sumarlos. `Decimal` conserva precisión; el formato monetario final se deja documentado sin imponer una política de redondeo no especificada.

## 3. Endpoints y separación de responsabilidades

`routers/` recibe HTTP, `schemas/` valida y documenta, `services/` consulta y aplica reglas, `models/` define la persistencia. FastAPI gestiona sesiones mediante `get_db()`.

- `POST /calculate-invoice` devuelve un resumen de los cuatro conceptos sin detallar todas las horas de EE2.
- `POST /calculate-concept` devuelve un concepto individual. En la versión presentada reutiliza `calcular_factura()`, por lo que internamente procesa los cuatro conceptos. Refactorización futura: cálculo realmente selectivo para reducir trabajo.
- `GET /client-statistics/{service_id}` calcula SUM/AVG/MAX/COUNT sobre la base y devuelve balance consumo−inyección.
- `GET /system-load` hace `GROUP BY record_timestamp`, suma consumos de los servicios y pagina con limit/offset.

No se inventó una tabla de clientes: el identificador disponible en los datos originales es `service_id`.

## 4. Calidad y pruebas

Se implementaron pruebas unitarias de reglas matemáticas y pruebas de integración para SQLAlchemy y endpoints. Los casos incluyen inyección mayor/igual/menor que consumo, fechas ordenadas, precios XM horarios, datos inválidos, paginación, 404 y 422. Las pruebas de integración dependen de una instancia local PostgreSQL con datos de septiembre de 2023.

Resultados de referencia: 3 servicios, 720 horas y 2.160 mediciones; consumo global del mes 30.713,113 kWh. Se usa `EXPLAIN ANALYZE` para investigar consultas relevantes, pero no se afirma un benchmarking completo o capacidad de grandes volúmenes a partir de este dataset pequeño.

## 5. Riesgos conocidos y mejoras futuras

1. Convertir la selección de tarifa en una consulta que detecte explícitamente cero o múltiples coincidencias, y ajustar la regla de CDI 2/3 con su índice único por nivel.
2. Evitar que `calculate-concept` calcule y cargue EE2 cuando solo se pide EA, EC o EE1.
3. Centralizar excepciones de negocio tipadas (en lugar de comparar texto de `ValueError`).
4. Añadir escenarios de integración con errores de datos: precio XM faltante, tarifas inexistentes y mediciones incompletas.
5. Añadir vigencia de tarifas si se soportan otros meses o cambios regulatorios.
6. Evaluar paginación por cursor para conjuntos grandes; índices y planes con `EXPLAIN (ANALYZE, BUFFERS)`.
7. Definir formalmente huso horario, políticas de facturación, redondeo y saldos negativos en un entorno productivo.
8. Autenticación, autorización, secretos gestionados, despliegue y monitoreo no se incluyen: fuera del alcance de la prueba local.

La implementación prioriza trazabilidad y consistencia sobre suposiciones no confirmadas. El diseño utiliza la muestra suministrada y declara sus límites.
