-- Consultas de solo lectura para revisión final (PostgreSQL).
-- Se ejecutan por separado en pgAdmin según necesidad.

-- 1. Filas esperadas: services=3, records=2160, consumption=2160,
-- injection=2160, tariffs=105, xm_data_hourly_per_agent=720.
SELECT 'services' AS tabla, COUNT(*) AS filas FROM services
UNION ALL SELECT 'records', COUNT(*) FROM records
UNION ALL SELECT 'consumption', COUNT(*) FROM consumption
UNION ALL SELECT 'injection', COUNT(*) FROM injection
UNION ALL SELECT 'tariffs', COUNT(*) FROM tariffs
UNION ALL SELECT 'xm_data_hourly_per_agent', COUNT(*) FROM xm_data_hourly_per_agent;

-- 2. Consumo agregado de septiembre 2023: 30713.113 kWh, 2160 mediciones.
SELECT COUNT(*) AS mediciones, SUM(c.value) AS consumo_total_kwh
FROM records r
JOIN consumption c ON c.id_record = r.id_record
WHERE r.record_timestamp >= '2023-09-01'
  AND r.record_timestamp < '2023-10-01';

-- 3. Integridad: deben devolver cero.
SELECT COUNT(*) AS registros_sin_consumo
FROM records r LEFT JOIN consumption c ON c.id_record = r.id_record
WHERE c.id_record IS NULL;

SELECT COUNT(*) AS registros_sin_inyeccion
FROM records r LEFT JOIN injection i ON i.id_record = r.id_record
WHERE i.id_record IS NULL;

SELECT id_service, record_timestamp, COUNT(*) AS repeticiones
FROM records GROUP BY id_service, record_timestamp HAVING COUNT(*) > 1;

-- 4. Revisión de tarifa efectiva por servicio (combinaciones únicas esperadas).
SELECT s.id_service, COUNT(t.id_tariff) AS tarifas_encontradas
FROM services s LEFT JOIN tariffs t
  ON s.id_market = t.id_market
 AND s.voltage_level = t.voltage_level
 AND ((s.voltage_level = 1 AND s.cdi = t.cdi)
      OR (s.voltage_level IN (2,3) AND t.cdi IS NULL))
GROUP BY s.id_service ORDER BY s.id_service;
