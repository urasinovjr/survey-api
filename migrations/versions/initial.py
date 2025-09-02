from alembic import op
import sqlalchemy as sa

revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('versions',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )
    op.create_table('questions',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('version_id', sa.Integer, sa.ForeignKey('versions.id'), nullable=False),
        sa.Column('number', sa.String, nullable=False),
        sa.Column('text', sa.String, nullable=False),
        sa.Column('type', sa.String, nullable=False),
        sa.Column('options', sa.String, nullable=True),
        sa.Column('constraints', sa.String, nullable=True),
    )
    op.create_table('responses',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('version_id', sa.Integer, sa.ForeignKey('versions.id'), nullable=False),
        sa.Column('question_id', sa.Integer, sa.ForeignKey('questions.id'), nullable=False),
        sa.Column('response_value', sa.String, nullable=False),
        sa.Column('response_timestamp', sa.DateTime, nullable=True),
    )

def downgrade():
    op.drop_table('responses')
    op.drop_table('questions')
    op.drop_table('versions')
