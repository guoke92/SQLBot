"""update default display brand

Revision ID: 075a1b2c3d4e5
Revises: 074a1b2c3d4e5
Create Date: 2026-07-27
"""

from alembic import op

revision = "075a1b2c3d4e5"
down_revision = "074a1b2c3d4e5"
branch_labels = None
depends_on = None

_DISPLAY_KEYS = (
    ("chat", "sqlbot_name"),
    ("appearance", "name"),
    ("appearance", "pc_welcome"),
    ("appearance", "pc_welcome_desc"),
    ("appearance", "slogan"),
)


def _replace_brand(old: str, new: str) -> None:
    predicates = " OR ".join(
        f"(ptype = '{ptype}' AND pkey = '{pkey}')"
        for ptype, pkey in _DISPLAY_KEYS
    )
    op.execute(
        "UPDATE sys_arg "
        f"SET pval = replace(pval, '{old}', '{new}') "
        f"WHERE ({predicates}) AND pval LIKE '%{old}%'"
    )


def upgrade() -> None:
    _replace_brand("SQLBot", "AI智能问数")


def downgrade() -> None:
    _replace_brand("AI智能问数", "SQLBot")
