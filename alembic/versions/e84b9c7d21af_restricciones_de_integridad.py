"""Agregar restricciones para energia no negativa y unicidad horaria.

Revision ID: e84b9c7d21af
Revises: c7a8f3e14b62

No elimina ni modifica registros. Requiere que no existan
valores negativos ni duplicados (ver consultas de prevalidacion).
"""

from alembic import op

revision = "e84b9c7d21af"
down_revision = "c7a8f3e14b62"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Aplica reglas de integridad al esquema PostgreSQL."""
    op.create_check_constraint(
        "ck_consumption_value_nonnegative", "consumption", "value >= 0"
    )
    op.create_check_constraint(
        "ck_injection_value_nonnegative", "injection", "value >= 0"
    )
    op.create_unique_constraint(
        "uq_records_service_timestamp",
        "records",
        ["id_service", "record_timestamp"],
    )


def downgrade() -> None:
    """Retira solo estas tres restricciones, sin borrar los datos."""
    op.drop_constraint(
        "uq_records_service_timestamp", "records", type_="unique"
    )
    op.drop_constraint(
        "ck_injection_value_nonnegative", "injection", type_="check"
    )
    op.drop_constraint(
        "ck_consumption_value_nonnegative", "consumption", type_="check"
    )
