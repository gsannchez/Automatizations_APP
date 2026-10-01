"""add template sort_order

Revision ID: c4a8e1f02b11
Revises: 2e9753f7794a
Create Date: 2026-06-02

"""
from alembic import op
import sqlalchemy as sa

revision = "c4a8e1f02b11"
down_revision = "2e9753f7794a"
branch_labels = None
depends_on = None

# Display order: viral/shorts first, then business, then long-form YouTube
_TEMPLATE_ORDER = {
    "Midnight Horror Tales": 10,
    "Stoic Wisdom Hub": 20,
    "Daily Business Hacks": 30,
    "Deep Mystery Chronicles": 40,
    "Future Tech Pulse": 50,
}


def upgrade() -> None:
    op.add_column(
        "template",
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="100"),
    )
    op.create_index("ix_template_sort_order", "template", ["sort_order"])

    for name, order in _TEMPLATE_ORDER.items():
        op.execute(
            sa.text("UPDATE template SET sort_order = :ord WHERE name = :name").bindparams(
                ord=order, name=name
            )
        )
    op.execute(
        sa.text(
            "UPDATE template SET sort_order = 900 WHERE name LIKE 'AutoTest%' OR name LIKE 'Test%'"
        )
    )


def downgrade() -> None:
    op.drop_index("ix_template_sort_order", table_name="template")
    op.drop_column("template", "sort_order")
