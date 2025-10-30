from **future** import annotations
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from plotty import **version**  # noqa
from plotty import **version** as _v  # noqa
from plotty import **version** as v  # noqa
from plotty import **version** as _  # noqa

config = context.config
if config.config_file_name:
fileConfig(config.config_file_name)

from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
metadata = MetaData()
devices = Table("devices", metadata,
Column("id", Integer, primary_key=True),
Column("kind", String, nullable=False),
Column("name", String), Column("port", String),
Column("firmware", String), Column("defaults_json", JSON),
Column("created_at", DateTime), Column("updated_at", DateTime),
)
pens = Table("pens", metadata,
Column("id", Integer, primary_key=True),
Column("name", String, unique=True),
Column("width_mm", Float), Column("speed_cap", Float),
Column("pressure", Integer), Column("passes", Integer),
Column("color_hex", String),
)
papers = Table("papers", metadata,
Column("id", Integer, primary_key=True),
Column("name", String, unique=True),
Column("width_mm", Float), Column("height_mm", Float),
Column("margin_mm", Float), Column("orientation", String),
)
jobs = Table("jobs", metadata,
Column("id", String, primary_key=True),
Column("name", String), Column("src_path", String),
Column("opt_path", String), Column("paper_id", Integer),
Column("state", String), Column("timings_json", JSON),
Column("metrics_json", JSON), Column("media_json", JSON),
Column("created_at", DateTime), Column("updated_at", DateTime),
)
layers = Table("layers", metadata,
Column("id", Integer, primary_key=True),
Column("job_id", String),
Column("layer_name", String), Column("order_index", Integer),
Column("pen_id", Integer), Column("stats_json", JSON),
Column("planned", Boolean),
)

target_metadata = metadata

def run_migrations_offline():
url = config.get_main_option("sqlalchemy.url")
context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
with context.begin_transaction():
context.run_migrations()

def run_migrations_online():
connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
with connectable.connect() as connection:
context.configure(connection=connection, target_metadata=target_metadata)
with context.begin_transaction():
context.run_migrations()

if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
