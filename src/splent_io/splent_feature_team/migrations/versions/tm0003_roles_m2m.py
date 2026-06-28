"""Team roles as many-to-many.

Adds a ``role`` table and a ``team_member_role`` pivot, migrates the old
free-text ``group`` of each member into an associated Role, copies the old
free-text ``role`` (job title) into a new ``position`` column, and drops the
``role``/``group`` columns. Existing members and their sections are preserved.

Revision ID: tm0003_roles_m2m
Revises: 3f76830b5164
"""

import re

import sqlalchemy as sa
from alembic import op

revision = "tm0003_roles_m2m"
down_revision = "3f76830b5164"
branch_labels = None
depends_on = None


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")


def upgrade():
    conn = op.get_bind()

    # 1. New free-text job title 'position', seeded from the old 'role' column.
    op.add_column(
        "team_member", sa.Column("position", sa.String(length=255), nullable=True)
    )
    op.execute("UPDATE team_member SET position = role")

    # 2. Role + association tables.
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("order", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_role_slug"), "role", ["slug"], unique=True)
    op.create_table(
        "team_member_role",
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["member_id"], ["team_member.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("member_id", "role_id"),
    )

    # 3. Data migration: one Role per distinct group, then associate members.
    rows = conn.execute(
        sa.text(
            "SELECT DISTINCT `group` FROM team_member "
            "WHERE `group` IS NOT NULL AND `group` <> ''"
        )
    ).fetchall()
    groups = [r[0] for r in rows]
    role_id = {}
    for i, g in enumerate(groups, start=1):
        slug = _slugify(g) or f"role-{i}"
        conn.execute(
            sa.text("INSERT INTO role (name, slug, `order`) VALUES (:n, :s, :o)"),
            {"n": g, "s": slug, "o": i},
        )
        role_id[g] = conn.execute(
            sa.text("SELECT id FROM role WHERE slug = :s"), {"s": slug}
        ).scalar()

    for mid, g in conn.execute(
        sa.text("SELECT id, `group` FROM team_member")
    ).fetchall():
        if g and g in role_id:
            conn.execute(
                sa.text(
                    "INSERT INTO team_member_role (member_id, role_id) VALUES (:m, :r)"
                ),
                {"m": mid, "r": role_id[g]},
            )

    # 4. Drop the now-migrated columns.
    op.drop_column("team_member", "role")
    op.drop_column("team_member", "group")


def downgrade():
    op.add_column(
        "team_member", sa.Column("group", sa.String(length=128), nullable=True)
    )
    op.add_column(
        "team_member", sa.Column("role", sa.String(length=255), nullable=True)
    )
    op.execute("UPDATE team_member SET role = position")
    op.drop_table("team_member_role")
    op.drop_index(op.f("ix_role_slug"), table_name="role")
    op.drop_table("role")
    op.drop_column("team_member", "position")
