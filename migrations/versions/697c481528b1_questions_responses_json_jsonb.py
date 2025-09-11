from alembic import op
import sqlalchemy as sa

# revision identifiers:
revision = "XXXX"  # <-- укажется автоматически
down_revision = "initial"  # или твоя последняя ревизия
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            ALTER TABLE questions
            ALTER COLUMN options TYPE JSONB
                USING CASE
                    WHEN options IS NULL OR trim(options::text) = '' THEN NULL
                    WHEN jsonb_typeof(options::jsonb) IS NOT NULL THEN options::jsonb
                    ELSE to_jsonb(options::text)
                END,
            ALTER COLUMN constraints TYPE JSONB
                USING CASE
                    WHEN constraints IS NULL OR trim(constraints::text) = '' THEN NULL
                    WHEN jsonb_typeof(constraints::jsonb) IS NOT NULL THEN constraints::jsonb
                    ELSE to_jsonb(constraints::text)
                END;
        """
        )
        op.execute(
            """
            ALTER TABLE responses
            ALTER COLUMN response_value TYPE JSONB
                USING CASE
                    WHEN response_value IS NULL OR trim(response_value::text) = '' THEN NULL
                    WHEN jsonb_typeof(response_value::jsonb) IS NOT NULL THEN response_value::jsonb
                    ELSE to_jsonb(response_value::text)
                END;
        """
        )
    elif bind.dialect.name == "sqlite":
        # Для SQLite менять физический тип не нужно — JSON сериализуется в TEXT.
        pass
    else:
        raise RuntimeError("Unsupported dialect")


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            ALTER TABLE responses
            ALTER COLUMN response_value TYPE TEXT USING response_value::text;
        """
        )
        op.execute(
            """
            ALTER TABLE questions
            ALTER COLUMN options TYPE TEXT USING options::text,
            ALTER COLUMN constraints TYPE TEXT USING constraints::text;
        """
        )
    elif bind.dialect.name == "sqlite":
        pass
    else:
        raise RuntimeError("Unsupported dialect")
