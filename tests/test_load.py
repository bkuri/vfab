#!/usr/bin/env python3
"""Load testing script for ploTTY with 100+ jobs."""

import time
import tempfile
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add ploTTY to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plotty.db import init_database, get_session
from plotty.models import Job, Paper


class LoadTestScenario:
    """Load testing scenario for ploTTY."""

    def __init__(self, num_jobs: int = 100):
        self.num_jobs = num_jobs
        self.temp_dir = Path(tempfile.mkdtemp(prefix="plotty_load_test_"))
        self.db_path = self.temp_dir / "test.db"
        self.results = {}

    def setup_test_environment(self):
        """Set up test environment with database and sample jobs."""
        print(f"🔧 Setting up load test environment with {self.num_jobs} jobs...")

        # Initialize database
        init_database(f"sqlite:///{self.db_path}")

        # Create test paper
        with get_session() as session:
            paper = Paper(
                name="Test Paper",
                width_mm=210.0,
                height_mm=297.0,
                margin_mm=10.0,
                orientation="portrait",
            )
            session.add(paper)
            session.commit()

            # Create test jobs
            for i in range(self.num_jobs):
                job = Job(
                    id=f"load_test_job_{i:03d}",
                    name=f"LoadTestJob_{i:03d}",
                    src_path=f"test_file_{i:03d}.svg",
                    paper_id=paper.id,
                    state="QUEUED",
                )
                session.add(job)

            session.commit()

        print(f"✅ Created {self.num_jobs} test jobs in database")

    def test_database_performance(self):
        """Test database performance with large number of jobs."""
        print("📊 Testing database performance...")

        with get_session() as session:
            # Test query performance
            start_time = time.time()

            # Test job listing
            jobs = session.query(Job).all()
            query_time = time.time() - start_time

            # Test filtering
            start_time = time.time()
            _ = session.query(Job).filter(Job.state == "QUEUED").all()
            filter_time = time.time() - start_time

            # Test pagination
            start_time = time.time()
            page_size = 20
            for page in range(0, len(jobs), page_size):
                _ = session.query(Job).offset(page).limit(page_size).all()
            pagination_time = time.time() - start_time

            self.results["database"] = {
                "total_jobs": len(jobs),
                "query_time": query_time,
                "filter_time": filter_time,
                "pagination_time": pagination_time,
                "jobs_per_second": len(jobs) / query_time if query_time > 0 else 0,
            }

            print("📈 Database Results:")
            print(f"   Total jobs: {len(jobs)}")
            print(f"   Query time: {query_time:.3f}s")
            print(f"   Filter time: {filter_time:.3f}s")
            print(f"   Pagination time: {pagination_time:.3f}s")
            print(f"   Jobs/second: {self.results['database']['jobs_per_second']:.0f}")

    def test_cli_performance(self):
        """Test CLI command performance with many jobs."""
        print("🖥️ Testing CLI performance...")

        commands_to_test = [
            (["list", "jobs"], "job_listing"),
            (["stats", "summary"], "stats_summary"),
            (["info", "system"], "system_info"),
        ]

        cli_results = {}

        for cmd, name in commands_to_test:
            start_time = time.time()

            try:
                result = subprocess.run(
                    [sys.executable, "-m", "plotty.cli"] + cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env={**os.environ, "PLOTTY_DB_PATH": str(self.db_path)},
                )

                execution_time = time.time() - start_time

                cli_results[name] = {
                    "execution_time": execution_time,
                    "returncode": result.returncode,
                    "stdout_length": len(result.stdout),
                    "stderr_length": len(result.stderr),
                }

                print(f"   {name}: {execution_time:.3f}s")

            except subprocess.TimeoutExpired:
                cli_results[name] = {
                    "execution_time": 30.0,
                    "returncode": -1,
                    "timeout": True,
                }
                print(f"   {name}: TIMEOUT (>30s)")

        self.results["cli"] = cli_results

    def test_memory_usage(self):
        """Test memory usage during operations."""
        print("💾 Testing memory usage...")

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform memory-intensive operations
        with get_session() as session:
            # Load all jobs into memory
            jobs = session.query(Job).all()

            # Simulate processing each job
            for job in jobs:
                # Simulate job data processing
                job_data = {
                    "id": job.id,
                    "name": job.name,
                    "state": job.state,
                    "src_path": job.src_path,
                }
                # Simulate some processing
                _ = len(str(job_data["name"]))

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory

        self.results["memory"] = {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_growth_mb": memory_growth,
            "memory_per_job_kb": (
                (memory_growth * 1024) / self.num_jobs if self.num_jobs > 0 else 0
            ),
        }

        print("💾 Memory Results:")
        print(f"   Initial: {initial_memory:.1f}MB")
        print(f"   Final: {final_memory:.1f}MB")
        print(f"   Growth: {memory_growth:.1f}MB")
        print(f"   Per job: {self.results['memory']['memory_per_job_kb']:.1f}KB")

    def test_concurrent_access(self):
        """Test concurrent access to ploTTY systems."""
        print("🔄 Testing concurrent access...")

        def worker_task(worker_id: int) -> Dict:
            """Worker task for concurrent testing."""
            start_time = time.time()

            try:
                with get_session() as session:
                    # Perform database operations
                    jobs = session.query(Job).limit(10).all()

                    # Simulate some processing
                    for job in jobs:
                        _ = job.name

                    execution_time = time.time() - start_time

                    return {
                        "worker_id": worker_id,
                        "execution_time": execution_time,
                        "jobs_processed": len(jobs),
                        "success": True,
                    }
            except Exception as e:
                return {
                    "worker_id": worker_id,
                    "execution_time": time.time() - start_time,
                    "error": str(e),
                    "success": False,
                }

        # Run concurrent workers
        num_workers = 10
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_task, i) for i in range(num_workers)]

            results = []
            for future in as_completed(futures):
                results.append(future.result())

        # Analyze concurrent results
        successful_workers = [r for r in results if r["success"]]
        failed_workers = [r for r in results if not r["success"]]

        if successful_workers:
            avg_execution_time = sum(
                r["execution_time"] for r in successful_workers
            ) / len(successful_workers)
            total_jobs_processed = sum(r["jobs_processed"] for r in successful_workers)
        else:
            avg_execution_time = 0
            total_jobs_processed = 0

        self.results["concurrent"] = {
            "num_workers": num_workers,
            "successful_workers": len(successful_workers),
            "failed_workers": len(failed_workers),
            "avg_execution_time": avg_execution_time,
            "total_jobs_processed": total_jobs_processed,
            "success_rate": len(successful_workers) / num_workers * 100,
        }

        print("🔄 Concurrent Results:")
        print(f"   Workers: {num_workers}")
        print(f"   Successful: {len(successful_workers)}/{num_workers}")
        print(f"   Success rate: {self.results['concurrent']['success_rate']:.1f}%")
        print(f"   Avg execution time: {avg_execution_time:.3f}s")

    def generate_load_report(self):
        """Generate comprehensive load test report."""
        print("\n" + "=" * 60)
        print("📊 PLOTTY LOAD TEST REPORT")
        print("=" * 60)

        # Database performance
        if "database" in self.results:
            db = self.results["database"]
            print("\n🗄️ Database Performance:")
            print(f"   Total jobs: {db['total_jobs']}")
            print(f"   Query time: {db['query_time']:.3f}s")
            print(f"   Jobs/second: {db['jobs_per_second']:.0f}")
            print(
                f"   Performance: {'✅ Excellent' if db['jobs_per_second'] > 1000 else '⚠️ Needs improvement' if db['jobs_per_second'] > 500 else '❌ Poor'}"
            )

        # CLI performance
        if "cli" in self.results:
            print("\n🖥️ CLI Performance:")
            for cmd_name, results in self.results["cli"].items():
                if "timeout" in results:
                    print(f"   {cmd_name}: ❌ TIMEOUT (>30s)")
                else:
                    status = (
                        "✅"
                        if results["execution_time"] < 2.0
                        else "⚠️" if results["execution_time"] < 5.0 else "❌"
                    )
                    print(f"   {cmd_name}: {status} {results['execution_time']:.3f}s")

        # Memory usage
        if "memory" in self.results:
            mem = self.results["memory"]
            print("\n💾 Memory Usage:")
            print(f"   Memory growth: {mem['memory_growth_mb']:.1f}MB")
            print(f"   Per job: {mem['memory_per_job_kb']:.1f}KB")
            print(
                f"   Efficiency: {'✅ Excellent' if mem['memory_per_job_kb'] < 10 else '⚠️ Acceptable' if mem['memory_per_job_kb'] < 50 else '❌ Poor'}"
            )

        # Concurrent access
        if "concurrent" in self.results:
            conc = self.results["concurrent"]
            print("\n🔄 Concurrent Access:")
            print(f"   Success rate: {conc['success_rate']:.1f}%")
            print(f"   Avg execution time: {conc['avg_execution_time']:.3f}s")
            print(
                f"   Reliability: {'✅ Excellent' if conc['success_rate'] > 95 else '⚠️ Acceptable' if conc['success_rate'] > 80 else '❌ Poor'}"
            )

        # Overall assessment
        print("\n🎯 Overall Assessment:")

        performance_score = 0
        max_score = 4

        # Database scoring
        if (
            "database" in self.results
            and self.results["database"]["jobs_per_second"] > 500
        ):
            performance_score += 1

        # CLI scoring
        if "cli" in self.results:
            cli_good = all(
                r.get("execution_time", 999) < 5.0 for r in self.results["cli"].values()
            )
            if cli_good:
                performance_score += 1

        # Memory scoring
        if (
            "memory" in self.results
            and self.results["memory"]["memory_per_job_kb"] < 50
        ):
            performance_score += 1

        # Concurrency scoring
        if (
            "concurrent" in self.results
            and self.results["concurrent"]["success_rate"] > 80
        ):
            performance_score += 1

        percentage = (performance_score / max_score) * 100
        status = (
            "✅ EXCELLENT"
            if percentage >= 75
            else "⚠️ ACCEPTABLE" if percentage >= 50 else "❌ NEEDS IMPROVEMENT"
        )

        print(
            f"   Performance Score: {performance_score}/{max_score} ({percentage:.0f}%)"
        )
        print(f"   Status: {status}")

        if percentage < 75:
            print("\n💡 Recommendations:")
            if (
                "database" in self.results
                and self.results["database"]["jobs_per_second"] < 500
            ):
                print("   - Add database indexes for better query performance")
            if (
                "memory" in self.results
                and self.results["memory"]["memory_per_job_kb"] > 50
            ):
                print("   - Optimize memory usage in job processing")
            if (
                "concurrent" in self.results
                and self.results["concurrent"]["success_rate"] < 80
            ):
                print("   - Improve concurrent access handling")

        print("=" * 60)

        return percentage >= 75

    def cleanup(self):
        """Clean up test environment."""
        try:
            import shutil

            shutil.rmtree(self.temp_dir)
            print("🧹 Cleaned up test environment")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

    def run_load_test(self) -> bool:
        """Run complete load test scenario."""
        print(f"🚀 Starting ploTTY load test with {self.num_jobs} jobs...")

        try:
            self.setup_test_environment()
            self.test_database_performance()
            self.test_cli_performance()
            self.test_memory_usage()
            self.test_concurrent_access()

            success = self.generate_load_report()

            return success

        except Exception as e:
            print(f"❌ Load test failed: {e}")
            import traceback

            traceback.print_exc()
            return False

        finally:
            self.cleanup()


def main():
    """Main load test entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="ploTTY Load Testing")
    parser.add_argument(
        "--jobs", type=int, default=100, help="Number of jobs to test with"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Run load test
    load_test = LoadTestScenario(num_jobs=args.jobs)
    success = load_test.run_load_test()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
