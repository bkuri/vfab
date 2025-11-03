from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = "0002_add_statistics_tables"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade():
    # Statistics configuration table
    op.create_table(
        "statistics_config",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("enabled", sa.Boolean, default=False, nullable=False),
        sa.Column("collection_level", sa.String, default="basic", nullable=False),
        sa.Column("retention_days", sa.Integer, default=365),
        sa.Column("auto_cleanup", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Job statistics table
    op.create_table(
        "job_statistics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("job_id", sa.String, sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("collection_level", sa.String, nullable=False),
        sa.Column(
            "event_type", sa.String, nullable=False
        ),  # created, started, finished, failed, etc.
        sa.Column(
            "timestamp", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column("duration_seconds", sa.Float),
        sa.Column("pen_changes", sa.Integer, default=0),
        sa.Column("distance_plotted_mm", sa.Float, default=0.0),
        sa.Column("distance_travel_mm", sa.Float, default=0.0),
        sa.Column("pen_down_time_seconds", sa.Float, default=0.0),
        sa.Column("pen_up_time_seconds", sa.Float, default=0.0),
        sa.Column("layers_completed", sa.Integer, default=0),
        sa.Column("total_layers", sa.Integer, default=0),
        sa.Column("metadata_json", sa.JSON),
        sa.Index("idx_job_statistics_job_id", "job_id"),
        sa.Index("idx_job_statistics_timestamp", "timestamp"),
        sa.Index("idx_job_statistics_event_type", "event_type"),
    )

    # Layer statistics table
    op.create_table(
        "layer_statistics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("job_id", sa.String, sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("layer_id", sa.Integer, sa.ForeignKey("layers.id"), nullable=False),
        sa.Column("pen_id", sa.Integer, sa.ForeignKey("pens.id")),
        sa.Column(
            "timestamp", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column("duration_seconds", sa.Float),
        sa.Column("distance_plotted_mm", sa.Float, default=0.0),
        sa.Column("distance_travel_mm", sa.Float, default=0.0),
        sa.Column("pen_down_time_seconds", sa.Float, default=0.0),
        sa.Column("pen_up_time_seconds", sa.Float, default=0.0),
        sa.Column("path_count", sa.Integer, default=0),
        sa.Column("point_count", sa.Integer, default=0),
        sa.Column("metadata_json", sa.JSON),
        sa.Index("idx_layer_statistics_job_id", "job_id"),
        sa.Index("idx_layer_statistics_layer_id", "layer_id"),
        sa.Index("idx_layer_statistics_pen_id", "pen_id"),
    )

    # System statistics table
    op.create_table(
        "system_statistics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "timestamp", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "stat_type", sa.String, nullable=False
        ),  # daily_summary, performance, etc.
        sa.Column("total_jobs", sa.Integer, default=0),
        sa.Column("completed_jobs", sa.Integer, default=0),
        sa.Column("failed_jobs", sa.Integer, default=0),
        sa.Column("total_plotting_time_seconds", sa.Float, default=0.0),
        sa.Column("total_distance_plotted_mm", sa.Float, default=0.0),
        sa.Column("total_pen_changes", sa.Integer, default=0),
        sa.Column("avg_job_duration_seconds", sa.Float),
        sa.Column("metadata_json", sa.JSON),
        sa.Index("idx_system_statistics_timestamp", "timestamp"),
        sa.Index("idx_system_statistics_type", "stat_type"),
    )

    # Performance metrics table
    op.create_table(
        "performance_metrics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("job_id", sa.String, sa.ForeignKey("jobs.id")),
        sa.Column(
            "timestamp", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column("metric_type", sa.String, nullable=False),  # speed, accuracy, etc.
        sa.Column("metric_value", sa.Float, nullable=False),
        sa.Column("unit", sa.String),
        sa.Column("context_json", sa.JSON),
        sa.Index("idx_performance_metrics_job_id", "job_id"),
        sa.Index("idx_performance_metrics_timestamp", "timestamp"),
        sa.Index("idx_performance_metrics_type", "metric_type"),
    )


def downgrade():
    op.drop_table("performance_metrics")
    op.drop_table("system_statistics")
    op.drop_table("layer_statistics")
    op.drop_table("job_statistics")
    op.drop_table("statistics_config")
