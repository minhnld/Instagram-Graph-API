"""update image_caption table

Revision ID: 5a6cce653bd9
Revises: 
Create Date: 2023-08-26 05:52:44.112326

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5a6cce653bd9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
FOREIGN_LANGUAGE_ID = "languages.id"


def upgrade() -> None:
    op.alter_column(
        "image_caption", "image_url", new_column_name="image_bucket_path_key"
    )
    op.add_column(
        "image_caption",
        sa.Column("language_id", sa.Integer, sa.ForeignKey(FOREIGN_LANGUAGE_ID)),
    )


def downgrade() -> None:
    op.drop_column("image_caption", "language")
