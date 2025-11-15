#!/usr/bin/env python3
"""
Database performance analysis and optimization for vfab.

This script analyzes database performance and suggests optimizations.
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from vfab.db import get_session
    from vfab.models import Job, Layer, Pen, Paper, JobStatistics
except ImportError as e:
    print(f"Error importing vfab modules: {e}")
    sys.exit(1)


def analyze_database_performance():
    """Analyze current database performance."""
    print("🔍 vfab Database Performance Analysis")
    print("=" * 50)

    try:
        # Get database session
        with get_session() as session:
            # Test basic query performance
            print("\n📊 Query Performance Tests:")

            # Test job listing
            start_time = time.time()
            jobs = session.query(Job).all()
            job_count = len(jobs)
            job_time = time.time() - start_time
            print(f"  Job listing ({job_count} jobs): {job_time:.4f}s")

            # Test job filtering by state
            start_time = time.time()
            active_jobs = (
                session.query(Job).filter(Job.state.in_(["queued", "running"])).all()
            )
            active_count = len(active_jobs)
            filter_time = time.time() - start_time
            print(f"  Active job filter ({active_count} jobs): {filter_time:.4f}s")

            # Test layer queries
            start_time = time.time()
            layers = session.query(Layer).all()
            layer_count = len(layers)
            layer_time = time.time() - start_time
            print(f"  Layer listing ({layer_count} layers): {layer_time:.4f}s")

            # Test job statistics queries
            start_time = time.time()
            stats = session.query(JobStatistics).all()
            stats_count = len(stats)
            stats_time = time.time() - start_time
            print(f"  Statistics listing ({stats_count} records): {stats_time:.4f}s")

            # Test complex join query
            start_time = time.time()
            _ = session.query(Job, Paper).join(Paper).limit(10).all()
            join_time = time.time() - start_time
            print(f"  Job-paper join (10 records): {join_time:.4f}s")

            # Analyze table sizes
            print("\n📏 Database Table Analysis:")

            # Get table counts
            job_count = session.query(Job).count()
            layer_count = session.query(Layer).count()
            pen_count = session.query(Pen).count()
            paper_count = session.query(Paper).count()
            stats_count = session.query(JobStatistics).count()

            print(f"  Jobs: {job_count} records")
            print(f"  Layers: {layer_count} records")
            print(f"  Pens: {pen_count} records")
            print(f"  Papers: {paper_count} records")
            print(f"  Statistics: {stats_count} records")

            # Performance assessment
            print("\n🎯 Performance Assessment:")

            # Query performance thresholds
            if job_time < 0.01:
                print("  ✅ Job listing: Excellent")
            elif job_time < 0.1:
                print("  ✅ Job listing: Good")
            else:
                print("  ⚠️  Job listing: Needs optimization")

            if filter_time < 0.01:
                print("  ✅ Job filtering: Excellent")
            elif filter_time < 0.05:
                print("  ✅ Job filtering: Good")
            else:
                print("  ⚠️  Job filtering: Needs optimization")

            if join_time < 0.01:
                print("  ✅ Join queries: Excellent")
            elif join_time < 0.05:
                print("  ✅ Join queries: Good")
            else:
                print("  ⚠️  Join queries: Needs optimization")

            # Database size assessment
            total_records = (
                job_count + layer_count + pen_count + paper_count + stats_count
            )

            if total_records < 1000:
                print("  ✅ Database size: Small (optimal)")
            elif total_records < 10000:
                print("  ✅ Database size: Medium (good)")
            else:
                print("  ⚠️  Database size: Large (consider indexing)")

            # Recommendations
            print("\n💡 Optimization Recommendations:")

            if job_count > 1000 and job_time > 0.01:
                print("  🔧 Consider adding index on Job.state")
                print("  🔧 Consider adding index on Job.created_at")

            if stats_count > 5000 and stats_time > 0.05:
                print("  🔧 Consider adding index on JobStatistics.timestamp")
                print("  🔧 Consider adding index on JobStatistics.job_id")

            if layer_count > 2000 and layer_time > 0.01:
                print("  🔧 Consider adding index on Layer.job_id")
                print("  🔧 Consider adding index on Layer.order_index")

            # Check for missing indexes that should exist
            print("\n🔍 Index Analysis:")

            # These are the indexes that should exist for good performance
            recommended_indexes = [
                "jobs.state",
                "jobs.created_at",
                "layers.job_id",
                "layers.order_index",
                "job_statistics.timestamp",
                "job_statistics.job_id",
                "papers.name",
            ]

            print("  Recommended indexes:")
            for index in recommended_indexes:
                print(f"    - {index}")

        print("\n🎉 Database analysis completed!")
        return True

    except Exception as e:
        print(f"❌ Database analysis failed: {e}")
        return False


def test_database_concurrency():
    """Test database performance under concurrent access."""
    print("\n🔄 Testing Database Concurrency...")

    try:
        import threading
        import queue

        with get_session() as session:
            job_count = session.query(Job).count()

        if job_count == 0:
            print("  ⚠️  No jobs found for concurrency test")
            return True

        results = queue.Queue()

        def worker():
            try:
                start_time = time.time()
                with get_session() as session:
                    _ = session.query(Job).limit(10).all()
                end_time = time.time()
                results.put(end_time - start_time)
            except Exception as e:
                results.put(e)

        # Run 5 concurrent queries
        threads = []
        start_time = time.time()

        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        total_time = time.time() - start_time

        # Collect results
        query_times = []
        errors = []

        while not results.empty():
            result = results.get()
            if isinstance(result, Exception):
                errors.append(result)
            else:
                query_times.append(result)

        if errors:
            print(f"  ❌ Concurrency errors: {len(errors)}")
            for error in errors:
                print(f"    {error}")
        else:
            avg_query_time = sum(query_times) / len(query_times)
            print(f"  ✅ Concurrent queries: {len(query_times)} successful")
            print(f"  📊 Average query time: {avg_query_time:.4f}s")
            print(f"  📊 Total time: {total_time:.4f}s")

            if avg_query_time < 0.1:
                print("  ✅ Concurrency performance: Excellent")
            elif avg_query_time < 0.5:
                print("  ✅ Concurrency performance: Good")
            else:
                print("  ⚠️  Concurrency performance: Needs optimization")

        return len(errors) == 0

    except Exception as e:
        print(f"  ❌ Concurrency test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        success1 = analyze_database_performance()
        success2 = test_database_concurrency()

        if success1 and success2:
            print("\n🎯 All database performance tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some database performance tests failed")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Database analysis interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Database analysis failed: {e}")
        sys.exit(1)
