"""Cambiar valores energéticos y tarifarios de FLOAT a NUMERIC.

Revision ID: c7a8f3e14b62
Revises: d42e7b6ac913

Esta migración conserva registros existentes. Las conversiones desde
FLOAT no reconstruyen por completo la precisión decimal original de los CSV.
"""
from alembic import op
import sqlalchemy as sa

revision = "c7a8f3e14b62"
down_revision = "d42e7b6ac913"
branch_labels = None
depends_on = None


COLUMNS = [
    ("consumption", "value", 18, 6),
    ("injection", "value", 18, 6),
    ("xm_data_hourly_per_agent", "value", 20, 10),
] + [
    ("tariffs", column, 18, 8)
    for column in ("G", "T", "D", "R", "C", "P", "CU")
]


def upgrade() -> None:
    # ALTER TABLE conserva las filas actuales y ajusta el tipo de columna.
    for table, column, precision, scale in COLUMNS:
        op.alter_column(
            table,
            column,
            existing_type=sa.Float(),
            type_=sa.Numeric(precision, scale),
            existing_nullable=False,
            postgresql_using=f'"{column}"::numeric({precision}, {scale})',
        )


def downgrade() -> None:
    # Revertir a FLOAT reintroduce aritmética aproximada.
    for table, column, precision, scale in reversed(COLUMNS):
        op.alter_column(
            table,
            column,
            existing_type=sa.Numeric(precision, scale),
            type_=sa.Float(),
            existing_nullable=False,
            postgresql_using=f'"{column}"::double precision',
        )
