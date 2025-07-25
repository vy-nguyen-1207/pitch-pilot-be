"""empty message

Revision ID: 563aee919336
Revises: 5d28b6a78c0b
Create Date: 2025-06-20 14:57:10.744341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '563aee919336'
down_revision: Union[str, Sequence[str], None] = '5d28b6a78c0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('training_results',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('training_id', sa.UUID(), nullable=False),
    sa.Column('eye_tracking_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Raw eye tracking metrics'),
    sa.Column('eye_tracking_total_score', sa.Float(), nullable=True, comment='Aggregated score from eye tracking'),
    sa.Column('audio_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Detailed metrics from audio analysis'),
    sa.Column('audio_total_score', sa.Float(), nullable=True, comment='Aggregated score from audio analysis'),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['training_id'], ['trainings.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('training_results')
    # ### end Alembic commands ###
