"""
Database models for vfab.

This module defines SQLAlchemy models for pens, papers, devices, jobs, and layers.
"""

from __future__ import annotations


from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class Device(Base):
    """Plotter device model."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    kind = Column(String, nullable=False)
    name = Column(String)
    port = Column(String)
    firmware = Column(String)
    defaults_json = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Pen(Base):
    """Pen model for different plotting tools."""

    __tablename__ = "pens"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    width_mm = Column(Float)
    speed_cap = Column(Float)
    pressure = Column(Integer)
    passes = Column(Integer)
    color_hex = Column(String)

    # Relationships
    layers = relationship("Layer", back_populates="pen")


class Paper(Base):
    """Paper size model."""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    width_mm = Column(Float, nullable=False)
    height_mm = Column(Float, nullable=False)
    margin_mm = Column(Float)
    orientation = Column(String)

    # Relationships
    jobs = relationship("Job", back_populates="paper")


class Job(Base):
    """Plotting job model."""

    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    name = Column(String)
    src_path = Column(String)
    opt_path = Column(String)
    paper_id = Column(Integer, ForeignKey("papers.id"))
    state = Column(String, nullable=False)
    timings_json = Column(JSON)
    metrics_json = Column(JSON)
    media_json = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    paper = relationship("Paper", back_populates="jobs")
    layers = relationship("Layer", back_populates="job")


class Layer(Base):
    """Layer model for multi-pen plotting."""

    __tablename__ = "layers"

    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    layer_name = Column(String, nullable=False)
    order_index = Column(Integer, nullable=False)
    pen_id = Column(Integer, ForeignKey("pens.id"))
    stats_json = Column(JSON)
    planned = Column(Boolean, default=False)

    # Relationships
    job = relationship("Job", back_populates="layers")
    pen = relationship("Pen", back_populates="layers")


class StatisticsConfig(Base):
    """Statistics configuration model."""

    __tablename__ = "statistics_config"

    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, default=False, nullable=False)
    collection_level = Column(String, default="basic", nullable=False)
    retention_days = Column(Integer, default=365)
    auto_cleanup = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class JobStatistics(Base):
    """Job statistics model."""

    __tablename__ = "job_statistics"

    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    collection_level = Column(String, nullable=False)
    event_type = Column(
        String, nullable=False
    )  # created, started, finished, failed, etc.
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    duration_seconds = Column(Float)
    pen_changes = Column(Integer, default=0)
    distance_plotted_mm = Column(Float, default=0.0)
    distance_travel_mm = Column(Float, default=0.0)
    pen_down_time_seconds = Column(Float, default=0.0)
    pen_up_time_seconds = Column(Float, default=0.0)
    layers_completed = Column(Integer, default=0)
    total_layers = Column(Integer, default=0)
    metadata_json = Column(JSON)

    # Relationships
    job = relationship("Job")


class LayerStatistics(Base):
    """Layer statistics model."""

    __tablename__ = "layer_statistics"

    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    layer_id = Column(Integer, ForeignKey("layers.id"), nullable=False)
    pen_id = Column(Integer, ForeignKey("pens.id"))
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    duration_seconds = Column(Float)
    distance_plotted_mm = Column(Float, default=0.0)
    distance_travel_mm = Column(Float, default=0.0)
    pen_down_time_seconds = Column(Float, default=0.0)
    pen_up_time_seconds = Column(Float, default=0.0)
    path_count = Column(Integer, default=0)
    point_count = Column(Integer, default=0)
    metadata_json = Column(JSON)

    # Relationships
    job = relationship("Job")
    layer = relationship("Layer")
    pen = relationship("Pen")


class SystemStatistics(Base):
    """System statistics model."""

    __tablename__ = "system_statistics"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    stat_type = Column(String, nullable=False)  # daily_summary, performance, etc.
    total_jobs = Column(Integer, default=0)
    completed_jobs = Column(Integer, default=0)
    failed_jobs = Column(Integer, default=0)
    total_plotting_time_seconds = Column(Float, default=0.0)
    total_distance_plotted_mm = Column(Float, default=0.0)
    total_pen_changes = Column(Integer, default=0)
    avg_job_duration_seconds = Column(Float)
    metadata_json = Column(JSON)


class PerformanceMetrics(Base):
    """Performance metrics model."""

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    metric_type = Column(String, nullable=False)  # speed, accuracy, etc.
    metric_value = Column(Float, nullable=False)
    unit = Column(String)
    context_json = Column(JSON)

    # Relationships
    job = relationship("Job")
