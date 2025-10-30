from **future** import annotations
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
op.create_table("devices",
sa.Column("id", sa.Integer, primary_key=True),
sa.Column("kind", sa.String, nullable=False),
sa.Column("name", sa.String),
sa.Column("port", sa.String),
sa.Column("firmware", sa.String),
sa.Column("defaults_json", sa.JSON),
sa.Column("created_at", sa.DateTime),
sa.Column("updated_at", sa.DateTime),
)
op.create_table("pens",
sa.Column("id", sa.Integer, primary_key=True),
sa.Column("name", sa.String, unique=True),
sa.Column("width_mm", sa.Float),
sa.Column("speed_cap", sa.Float),
sa.Column("pressure", sa.Integer),
sa.Column("passes", sa.Integer),
sa.Column("color_hex", sa.String),
)
op.create_table("papers",
sa.Column("id", sa.Integer, primary_key=True),
sa.Column("name", sa.String, unique=True),
sa.Column("width_mm", sa.Float),
sa.Column("height_mm", sa.Float),
sa.Column("margin_mm", sa.Float),
sa.Column("orientation", sa.String),
)
op.create_table("jobs",
sa.Column("id", sa.String, primary_key=True),
sa.Column("name", sa.String),
sa.Column("src_path", sa.String),
sa.Column("opt_path", sa.String),
sa.Column("paper_id", sa.Integer),
sa.Column("state", sa.String),
sa.Column("timings_json", sa.JSON),
sa.Column("metrics_json", sa.JSON),
sa.Column("media_json", sa.JSON),
sa.Column("created_at", sa.DateTime),
sa.Column("updated_at", sa.DateTime),
)
op.create_table("layers",
sa.Column("id", sa.Integer, primary_key=True),
sa.Column("job_id", sa.String),
sa.Column("layer_name", sa.String),
sa.Column("order_index", sa.Integer),
sa.Column("pen_id", sa.Integer),
sa.Column("stats_json", sa.JSON),
sa.Column("planned", sa.Boolean),
)

def downgrade():
for t in ("layers","jobs","papers","pens","devices"):
op.drop_table(t)
