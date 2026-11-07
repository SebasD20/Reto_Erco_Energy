"""Permitir tarifas sin CDI en niveles de tensión 2 y 3.

Revision ID: d42e7b6ac913
Revises: b77fa6dac186
Create Date: 2026-11-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d42e7b6ac913"
down_revision: Union[str, Sequence[str], None] = "b77fa6dac186"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for foreign_key in inspector.get_foreign_keys("services"):
        if foreign_key["constrained_columns"] == ["id_market", "cdi", "voltage_level"]:
            op.drop_constraint(foreign_key["name"], "services", type_="foreignkey")
            break

    primary_key = inspector.get_pk_constraint("tariffs")
    op.drop_constraint(primary_key["name"], "tariffs", type_="primary")
    op.add_column(
        "tariffs",
        sa.Column("id_tariff", sa.Integer(), sa.Identity(), nullable=False),
    )
    op.create_primary_key("pk_tariffs", "tariffs", ["id_tariff"])
    op.alter_column(
        "tariffs",
        "cdi",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.create_index(
        "uq_tariffs_market_voltage_cdi",
        "tariffs",
        ["id_market", "voltage_level", "cdi"],
        unique=True,
        postgresql_where=sa.text("cdi IS NOT NULL"),
    )
    op.create_index(
        "uq_tariffs_market_voltage_no_cdi",
        "tariffs",
        ["id_market", "voltage_level"],
        unique=True,
        postgresql_where=sa.text("cdi IS NULL"),
    )


def downgrade() -> None:
    bind = op.get_bind()
    has_null_cdi = bind.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM tariffs WHERE cdi IS NULL)")
    ).scalar_one()
    if has_null_cdi:
        raise RuntimeError("No se puede revertir: existen tarifas con cdi NULL.")

    op.drop_index("uq_tariffs_market_voltage_no_cdi", table_name="tariffs")
    op.drop_index("uq_tariffs_market_voltage_cdi", table_name="tariffs")
    op.drop_constraint("pk_tariffs", "tariffs", type_="primary")
    op.drop_column("tariffs", "id_tariff")
    op.alter_column(
        "tariffs",
        "cdi",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_primary_key(
        "tariffs_pkey",
        "tariffs",
        ["id_market", "cdi", "voltage_level"],
    )
    op.create_foreign_key(
        "services_id_market_fkey",
        "services",
        "tariffs",
        ["id_market", "cdi", "voltage_level"],
        ["id_market", "cdi", "voltage_level"],
    )