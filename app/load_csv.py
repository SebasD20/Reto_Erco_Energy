from pathlib import Path

from sqlalchemy import text

from app.db import engine

DATA_DIR = Path("data")

# (tabla, archivo, columnas en el MISMO orden que tiene el CSV)
CARGAS = [
    ("tariffs", "tariffs.csv",
        ["id_market", "voltage_level", "cdi", "G", "T", "D", "R", "C", "P", "CU"]),
    ("services", "services.csv",
     ["id_service", "id_market", "cdi", "voltage_level"]),
    ("xm_data_hourly_per_agent", "xm_data_hourly_per_agent.csv",
     ["record_timestamp", "value"]),
    ("records", "records.csv",
     ["id_record", "id_service", "record_timestamp"]),
    ("injection", "injection.csv", ["id_record", "value"]),
    ("consumption", "consumption.csv", ["id_record", "value"]),
]

def cargar_csv(conn, tabla, archivo, columnas):
    cols = ", ".join(f'"{c}"' for c in columnas)
    sql = f'COPY {tabla} ({cols}) FROM STDIN WITH (FORMAT csv, HEADER true)'
    raw = conn.connection.driver_connection  # conexión nativa de psycopg
    with raw.cursor() as cur, cur.copy(sql) as copy:
        with open(DATA_DIR / archivo, "rb") as f:
            while chunk := f.read(1024 * 1024):
                copy.write(chunk)
    print(f"OK: {tabla}")


def ajustar_secuencias(conn):
    # Necesario si los CSV traen los ids explícitos
    for tabla, col in [("services", "id_service"), ("records", "id_record")]:
        conn.execute(text(
            f"SELECT setval(pg_get_serial_sequence('{tabla}', '{col}'), "
            f"COALESCE((SELECT MAX({col}) FROM {tabla}), 1))"
        ))


def main():
    with engine.begin() as conn:  # una sola transacción: si algo falla, no queda nada a medias
        for tabla, archivo, columnas in CARGAS:
            cargar_csv(conn, tabla, archivo, columnas)
        ajustar_secuencias(conn)
    print("Carga completa")


if __name__ == "__main__":
    main()