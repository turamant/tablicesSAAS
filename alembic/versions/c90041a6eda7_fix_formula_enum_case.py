"""fix formula enum case

Revision ID: c90041a6eda7
Revises: 41be8bec823c
Create Date: 2026-03-07 17:30:20.039036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c90041a6eda7'
down_revision: Union[str, Sequence[str], None] = '41be8bec823c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Создаем новый enum с верхним регистром
    op.execute("CREATE TYPE fieldtype_new AS ENUM ('TEXT', 'NUMBER', 'DATE', 'BOOLEAN', 'SELECT', 'MULTISELECT', 'EMAIL', 'FORMULA')")
    op.execute("ALTER TABLE fields ALTER COLUMN field_type TYPE fieldtype_new USING field_type::text::fieldtype_new")
    op.execute("DROP TYPE fieldtype")
    op.execute("ALTER TYPE fieldtype_new RENAME TO fieldtype")

def downgrade():
    op.execute("CREATE TYPE fieldtype_old AS ENUM ('TEXT', 'NUMBER', 'DATE', 'BOOLEAN', 'SELECT', 'MULTISELECT', 'EMAIL')")
    op.execute("UPDATE fields SET field_type = 'TEXT' WHERE field_type = 'FORMULA'")
    op.execute("ALTER TABLE fields ALTER COLUMN field_type TYPE fieldtype_old USING field_type::text::fieldtype_old")
    op.execute("DROP TYPE fieldtype")
    op.execute("ALTER TYPE fieldtype_old RENAME TO fieldtype")
