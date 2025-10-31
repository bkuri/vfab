"""
Database models for ploTTY.

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
