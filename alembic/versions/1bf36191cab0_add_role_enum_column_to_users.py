"""add role enum column to users

Revision ID: 1bf36191cab0
Revises: 2d9b1a7662f8
Create Date: 2026-03-18 15:13:15.367069

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1bf36191cab0"
down_revision: Union[str, Sequence[str], None] = "2d9b1a7662f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_role = sa.Enum("user", "admin", "superadmin", name="user_role")
    user_role.create(op.get_bind())
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("user", "admin", "superadmin", name="user_role"),
            nullable=True,
        ),
    )
    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")
    op.alter_column("users", "role", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "role")
    sa.Enum(name="user_role").drop(op.get_bind())
