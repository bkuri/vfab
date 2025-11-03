"""
Statistics service for ploTTY.

This module provides database-backed statistics collection and retrieval
for jobs, layers, and system performance metrics.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import (
    Job,
    Pen,
    Paper,
    JobStatistics,
    LayerStatistics,
    SystemStatistics,
    PerformanceMetrics,
    StatisticsConfig,
)
from .db import get_session


class StatisticsService:
    """Service for collecting and retrieving plotting statistics."""

    def __init__(self):
        self.session_context = get_session()

    def record_job_event(
        self,
        job_id: str,
        event_type: str,
        duration_seconds: Optional[float] = None,
        pen_changes: int = 0,
        distance_plotted_mm: float = 0.0,
        distance_travel_mm: float = 0.0,
        pen_down_time_seconds: float = 0.0,
        pen_up_time_seconds: float = 0.0,
        layers_completed: int = 0,
        total_layers: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JobStatistics:
        """Record a job lifecycle event.

        Args:
            job_id: Unique job identifier
            event_type: Type of event (created, started, finished, failed, etc.)
            duration_seconds: Event duration in seconds
            pen_changes: Number of pen changes during event
            distance_plotted_mm: Distance plotted with pen down
            distance_travel_mm: Total distance traveled
            pen_down_time_seconds: Time with pen down
            pen_up_time_seconds: Time with pen up
            layers_completed: Number of layers completed
            total_layers: Total number of layers in job
            metadata: Additional event metadata

        Returns:
            Created JobStatistics record
        """
        with self.session_context as session:
            # Get collection level from config
            config = session.query(StatisticsConfig).first()
            collection_level = config.collection_level if config else "basic"

            job_stat = JobStatistics(
                job_id=job_id,
                collection_level=collection_level,
                event_type=event_type,
                timestamp=datetime.utcnow(),
                duration_seconds=duration_seconds,
                pen_changes=pen_changes,
                distance_plotted_mm=distance_plotted_mm,
                distance_travel_mm=distance_travel_mm,
                pen_down_time_seconds=pen_down_time_seconds,
                pen_up_time_seconds=pen_up_time_seconds,
                layers_completed=layers_completed,
                total_layers=total_layers,
                metadata_json=metadata,
            )

            session.add(job_stat)
            session.flush()  # Get the ID without committing

            # Update system statistics for daily summary
            self._update_daily_summary(session, event_type)

            return job_stat

    def record_layer_stats(
        self,
        job_id: str,
        layer_id: int,
        pen_id: Optional[int],
        duration_seconds: Optional[float],
        distance_plotted_mm: float = 0.0,
        distance_travel_mm: float = 0.0,
        pen_down_time_seconds: float = 0.0,
        pen_up_time_seconds: float = 0.0,
        path_count: int = 0,
        point_count: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LayerStatistics:
        """Record layer-specific statistics.

        Args:
            job_id: Parent job ID
            layer_id: Layer ID
            pen_id: Pen used for this layer
            duration_seconds: Layer plotting duration
            distance_plotted_mm: Distance plotted with pen down
            distance_travel_mm: Total distance traveled
            pen_down_time_seconds: Time with pen down
            pen_up_time_seconds: Time with pen up
            path_count: Number of paths in layer
            point_count: Number of points in layer
            metadata: Additional layer metadata

        Returns:
            Created LayerStatistics record
        """
        with self.session_context as session:
            layer_stat = LayerStatistics(
                job_id=job_id,
                layer_id=layer_id,
                pen_id=pen_id,
                timestamp=datetime.utcnow(),
                duration_seconds=duration_seconds,
                distance_plotted_mm=distance_plotted_mm,
                distance_travel_mm=distance_travel_mm,
                pen_down_time_seconds=pen_down_time_seconds,
                pen_up_time_seconds=pen_up_time_seconds,
                path_count=path_count,
                point_count=point_count,
                metadata_json=metadata,
            )

            session.add(layer_stat)
            session.flush()

            return layer_stat

    def record_performance_metric(
        self,
        job_id: Optional[str],
        metric_type: str,
        metric_value: float,
        unit: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> PerformanceMetrics:
        """Record a performance metric.

        Args:
            job_id: Associated job ID (optional)
            metric_type: Type of metric (speed, accuracy, etc.)
            metric_value: Metric value
            unit: Unit of measurement
            context: Additional context

        Returns:
            Created PerformanceMetrics record
        """
        with self.session_context as session:
            metric = PerformanceMetrics(
                job_id=job_id,
                timestamp=datetime.utcnow(),
                metric_type=metric_type,
                metric_value=metric_value,
                unit=unit,
                context_json=context,
            )

            session.add(metric)
            session.flush()

            return metric

    def get_job_summary_stats(self) -> Dict[str, Any]:
        """Get comprehensive job statistics summary.

        Returns:
            Dictionary with job statistics
        """
        with self.session_context as session:
            # Get job counts by state
            job_states_result = (
                session.query(Job.state, func.count(Job.id)).group_by(Job.state).all()
            )
            by_state = {state: count for state, count in job_states_result}

            # Get total counts
            total_jobs = session.query(func.count(Job.id)).scalar() or 0
            completed_jobs = by_state.get("COMPLETED", 0)
            failed_jobs = by_state.get("FAILED", 0)

            # Get job timing statistics
            completed_job_stats = (
                session.query(
                    func.avg(JobStatistics.duration_seconds),
                    func.sum(JobStatistics.duration_seconds),
                )
                .join(Job)
                .filter(
                    Job.state == "COMPLETED",
                    JobStatistics.event_type == "finished",
                )
                .first()
            )

            avg_time = float(completed_job_stats[0] or 0.0)
            total_time = float(completed_job_stats[1] or 0.0)

            # Get job age range
            oldest_newest = session.query(
                func.min(Job.created_at),
                func.max(Job.created_at),
            ).first()

            # Get paper usage statistics
            paper_stats_result = (
                session.query(Paper.name, func.count(Job.id))
                .join(Job)
                .group_by(Paper.name)
                .all()
            )
            by_paper = {paper: count for paper, count in paper_stats_result}

            # Calculate success rate
            success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0

            return {
                "total_jobs": total_jobs,
                "completed_jobs": completed_jobs,
                "failed_jobs": failed_jobs,
                "by_state": by_state,
                "by_paper": by_paper,
                "success_rate": success_rate,
                "avg_time": avg_time,
                "total_time": total_time,
                "oldest_job": oldest_newest[0],
                "newest_job": oldest_newest[1],
            }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance analytics.

        Returns:
            Dictionary with performance statistics
        """
        with self.session_context as session:
            # Get time-based statistics
            time_stats_result = (
                session.query(
                    func.sum(JobStatistics.duration_seconds).label("total_time"),
                    func.avg(JobStatistics.duration_seconds).label("avg_time"),
                    func.count(JobStatistics.id).label("completed_count"),
                )
                .filter(JobStatistics.event_type == "finished")
                .first()
            )

            total_time = float(time_stats_result.total_time or 0.0)
            avg_time = float(time_stats_result.avg_time or 0.0)
            completed_count = int(time_stats_result.completed_count or 0)

            # Get job age span
            job_age_result = session.query(
                func.min(Job.created_at).label("oldest"),
                func.max(Job.created_at).label("newest"),
            ).first()

            # Get recent performance metrics
            recent_metrics = (
                session.query(PerformanceMetrics)
                .filter(
                    PerformanceMetrics.timestamp
                    >= datetime.utcnow() - timedelta(days=7)
                )
                .order_by(PerformanceMetrics.timestamp.desc())
                .limit(10)
                .all()
            )

            return {
                "total_plotting_time": total_time,
                "average_job_time": avg_time,
                "completed_jobs": completed_count,
                "oldest_job": job_age_result.oldest,
                "newest_job": job_age_result.newest,
                "recent_metrics": [
                    {
                        "type": metric.metric_type,
                        "value": metric.metric_value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp,
                    }
                    for metric in recent_metrics
                ],
            }

    def get_pen_usage_stats(self) -> Dict[str, Any]:
        """Get pen usage statistics.

        Returns:
            Dictionary with pen usage analytics
        """
        with self.session_context as session:
            # Get pen usage from layer statistics
            pen_stats_result = (
                session.query(
                    Pen.name,
                    func.sum(LayerStatistics.distance_plotted_mm).label(
                        "total_distance"
                    ),
                    func.sum(LayerStatistics.pen_down_time_seconds).label(
                        "pen_down_time"
                    ),
                    func.count(LayerStatistics.id).label("layer_count"),
                )
                .join(LayerStatistics, Pen.id == LayerStatistics.pen_id)
                .group_by(Pen.id, Pen.name)
                .all()
            )

            return {
                "pen_usage": [
                    {
                        "pen_name": stat.name,
                        "total_distance_mm": float(stat.total_distance or 0.0),
                        "pen_down_time_seconds": float(stat.pen_down_time or 0.0),
                        "layers_plotted": int(stat.layer_count or 0),
                    }
                    for stat in pen_stats_result
                ]
            }

    def _update_daily_summary(self, session: Session, event_type: str) -> None:
        """Update daily system statistics.

        Args:
            session: Database session
            event_type: Type of job event that occurred
        """
        today = datetime.utcnow().date()

        # Get or create today's summary
        summary = (
            session.query(SystemStatistics)
            .filter(
                SystemStatistics.stat_type == "daily_summary",
                func.date(SystemStatistics.timestamp) == today,
            )
            .first()
        )

        if not summary:
            summary = SystemStatistics(
                stat_type="daily_summary",
                timestamp=datetime.utcnow(),
                total_jobs=0,
                completed_jobs=0,
                failed_jobs=0,
                total_plotting_time_seconds=0.0,
                total_distance_plotted_mm=0.0,
                total_pen_changes=0,
            )
            session.add(summary)

        # Update counters based on event type
        if event_type in ["created", "queued"]:
            summary.total_jobs = (summary.total_jobs or 0) + 1
        elif event_type == "finished":
            summary.completed_jobs = (summary.completed_jobs or 0) + 1
        elif event_type == "failed":
            summary.failed_jobs = (summary.failed_jobs or 0) + 1

    def configure_statistics(
        self,
        enabled: bool = True,
        collection_level: str = "basic",
        retention_days: int = 365,
        auto_cleanup: bool = True,
    ) -> StatisticsConfig:
        """Configure statistics collection settings.

        Args:
            enabled: Whether statistics collection is enabled
            collection_level: Level of detail to collect (basic, detailed, full)
            retention_days: Days to retain statistics
            auto_cleanup: Whether to automatically cleanup old statistics

        Returns:
            Updated StatisticsConfig record
        """
        with self.session_context as session:
            config = session.query(StatisticsConfig).first()

            if not config:
                config = StatisticsConfig()
                session.add(config)

            config.enabled = enabled
            config.collection_level = collection_level
            config.retention_days = retention_days
            config.auto_cleanup = auto_cleanup

            return config

    def cleanup_old_statistics(self, retention_days: Optional[int] = None) -> int:
        """Clean up statistics older than retention period.

        Args:
            retention_days: Days to retain (uses config if not provided)

        Returns:
            Number of records cleaned up
        """
        with self.session_context as session:
            # Get retention days from config if not provided
            if retention_days is None:
                config = session.query(StatisticsConfig).first()
                retention_days = int(config.retention_days if config else 365)

            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

            # Clean up old statistics
            deleted_count = 0

            # Delete old job statistics
            deleted_count += (
                session.query(JobStatistics)
                .filter(JobStatistics.timestamp < cutoff_date)
                .delete()
            )

            # Delete old layer statistics
            deleted_count += (
                session.query(LayerStatistics)
                .filter(LayerStatistics.timestamp < cutoff_date)
                .delete()
            )

            # Delete old performance metrics
            deleted_count += (
                session.query(PerformanceMetrics)
                .filter(PerformanceMetrics.timestamp < cutoff_date)
                .delete()
            )

            # Delete old system statistics (keep daily summaries longer)
            system_cutoff = datetime.utcnow() - timedelta(days=retention_days * 2)
            deleted_count += (
                session.query(SystemStatistics)
                .filter(
                    SystemStatistics.timestamp < system_cutoff,
                    SystemStatistics.stat_type != "daily_summary",
                )
                .delete()
            )

            return deleted_count


# Global statistics service instance
_stats_service = None


def get_statistics_service() -> StatisticsService:
    """Get the global statistics service instance.

    Returns:
        StatisticsService instance
    """
    global _stats_service
    if _stats_service is None:
        _stats_service = StatisticsService()
    return _stats_service
