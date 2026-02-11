"""initial schema

Revision ID: 202602110001
Revises:
Create Date: 2026-02-11
"""

import sqlalchemy as sa
from alembic import op

revision = "202602110001"
down_revision = None
branch_labels = None
depends_on = None


split_type_enum = sa.Enum("amount", "percentage", name="split_type_enum")
participant_type_enum = sa.Enum("user", "friend", name="participant_type_enum")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "friends",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_friends_name"), "friends", ["name"], unique=False)
    op.create_index(op.f("ix_friends_owner_id"), "friends", ["owner_id"], unique=False)

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "name", name="uq_category_owner_name"),
    )
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=False)
    op.create_index(op.f("ix_categories_owner_id"), "categories", ["owner_id"], unique=False)

    op.create_table(
        "groups",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "name", name="uq_group_owner_name"),
    )
    op.create_index(op.f("ix_groups_name"), "groups", ["name"], unique=False)
    op.create_index(op.f("ix_groups_owner_id"), "groups", ["owner_id"], unique=False)

    split_type_enum.create(op.get_bind(), checkfirst=True)
    participant_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "expenses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("group_id", sa.Uuid(), nullable=True),
        sa.Column("split_type", split_type_enum, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_expenses_description"), "expenses", ["description"], unique=False)
    op.create_index(op.f("ix_expenses_owner_id"), "expenses", ["owner_id"], unique=False)

    op.create_table(
        "expense_splits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("expense_id", sa.Uuid(), nullable=False),
        sa.Column("participant_type", participant_type_enum, nullable=False),
        sa.Column("participant_user_id", sa.Uuid(), nullable=True),
        sa.Column("participant_friend_id", sa.Uuid(), nullable=True),
        sa.Column("share_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("share_percentage", sa.Numeric(7, 4), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["expense_id"], ["expenses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["participant_friend_id"], ["friends.id"]),
        sa.ForeignKeyConstraint(["participant_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_expense_splits_expense_id"), "expense_splits", ["expense_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_expense_splits_expense_id"), table_name="expense_splits")
    op.drop_table("expense_splits")
    op.drop_index(op.f("ix_expenses_owner_id"), table_name="expenses")
    op.drop_index(op.f("ix_expenses_description"), table_name="expenses")
    op.drop_table("expenses")
    op.drop_index(op.f("ix_groups_owner_id"), table_name="groups")
    op.drop_index(op.f("ix_groups_name"), table_name="groups")
    op.drop_table("groups")
    op.drop_index(op.f("ix_categories_owner_id"), table_name="categories")
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_table("categories")
    op.drop_index(op.f("ix_friends_owner_id"), table_name="friends")
    op.drop_index(op.f("ix_friends_name"), table_name="friends")
    op.drop_table("friends")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    participant_type_enum.drop(op.get_bind(), checkfirst=True)
    split_type_enum.drop(op.get_bind(), checkfirst=True)
