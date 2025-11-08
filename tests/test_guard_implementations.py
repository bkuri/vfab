#!/usr/bin/env python3
"""Unit tests for new guard implementations."""

import sys
import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plotty.guards.job_guards import PaperSessionGuard, PenLayerGuard
from plotty.guards.system_guards import CameraGuard
from plotty.guards.base import GuardResult
from plotty.config import Settings
from plotty.db import init_database, get_session
from plotty.models import Job, Paper, Pen, Layer


def test_paper_session_guard():
    """Test PaperSessionGuard implementation."""
    print("Testing PaperSessionGuard...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Initialize test database
        db_path = Path(tmp_dir) / "test.db"
        db_url = f"sqlite:///{db_path}"
        init_database(db_url)

        # Set config env var for database
        import os

        os.environ["PLOTTY_CONFIG"] = str(Path(tmp_dir) / "config.yaml")

        # Create test config
        config = Settings()
        config.database.url = db_url

        # Create guard
        guard = PaperSessionGuard(config)

        with get_session() as session:
            # Create test paper
            paper = Paper(
                name="Test Paper", width_mm=210.0, height_mm=297.0, margin_mm=10.0
            )
            session.add(paper)
            session.commit()

            # Test 1: Non-existent job
            result = guard.check("nonexistent_job")
            print(f"  Non-existent job: {result.result.value} - {result.message}")
            assert result.result.value == "fail"

            # Test 2: Job without paper
            job_no_paper = Job(id="job_no_paper", state="NEW")
            session.add(job_no_paper)
            session.commit()

            result = guard.check("job_no_paper")
            print(f"  Job without paper: {result.result.value} - {result.message}")
            assert result.result.value == "fail"

            # Test 3: Job with paper, no conflicts
            job_with_paper = Job(id="job_with_paper", state="NEW", paper_id=paper.id)
            session.add(job_with_paper)
            session.commit()

            result = guard.check("job_with_paper")
            print(
                f"  Job with available paper: {result.result.value} - {result.message}"
            )
            assert result.result.value == "pass"

            # Test 4: Conflicting job
            conflicting_job = Job(
                id="conflicting_job", state="QUEUED", paper_id=paper.id  # Active state
            )
            session.add(conflicting_job)
            session.commit()

            result = guard.check("job_with_paper")
            print(
                f"  Job with conflicting paper: {result.result.value} - {result.message}"
            )
            assert result.result.value == "fail"

    print("  ✓ PaperSessionGuard tests passed")


def test_pen_layer_guard():
    """Test PenLayerGuard implementation."""
    print("Testing PenLayerGuard...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Initialize test database
        db_path = Path(tmp_dir) / "test.db"
        db_url = f"sqlite:///{db_path}"
        init_database(db_url)

        # Set config env var for database
        import os

        os.environ["PLOTTY_CONFIG"] = str(Path(tmp_dir) / "config.yaml")

        # Create test config
        config = Settings()
        config.database.url = db_url

        # Create guard
        guard = PenLayerGuard(config)

        with get_session() as session:
            # Create test pen
            pen = Pen(
                name="Test Pen", width_mm=0.3, speed_cap=50.0, pressure=30, passes=1
            )
            session.add(pen)
            session.commit()

            # Create test job
            job = Job(id="pen_test_job", state="NEW")
            session.add(job)
            session.commit()

            # Test 1: Job without layers
            result = guard.check("pen_test_job")
            print(f"  Job without layers: {result.result.value} - {result.message}")
            assert result.result.value == "soft_fail"

            # Test 2: Layer without pen
            layer_no_pen = Layer(
                job_id="pen_test_job",
                layer_name="No Pen Layer",
                order_index=0,
                pen_id=None,
            )
            session.add(layer_no_pen)
            session.commit()

            result = guard.check("pen_test_job")
            print(f"  Layer without pen: {result.result.value} - {result.message}")
            assert result.result.value == "fail"

            # Test 3: Layer with valid pen
            layer_with_pen = Layer(
                job_id="pen_test_job",
                layer_name="Valid Pen Layer",
                order_index=1,
                pen_id=pen.id,
            )
            session.add(layer_with_pen)
            session.commit()

            result = guard.check("pen_test_job")
            print(f"  Mixed pen assignments: {result.result.value} - {result.message}")
            assert (
                result.result.value == "soft_fail"
            )  # Some layers compatible, some not

            # Test 4: All layers with valid pens
            layer_no_pen.pen_id = pen.id
            session.commit()

            result = guard.check("pen_test_job")
            print(f"  All layers compatible: {result.result.value} - {result.message}")
            assert result.result.value == "pass"

            # Test 5: Layer with non-existent pen
            session.query(Layer).filter(Layer.id == layer_with_pen.id).update(
                {"pen_id": 999}
            )
            session.commit()

            result = guard.check("pen_test_job")
            print(f"  Non-existent pen: {result.result.value} - {result.message}")
            # With 1 compatible layer and 1 with non-existent pen, this should be soft_fail
            assert result.result.value == "soft_fail"

    print("  ✓ PenLayerGuard tests passed")


def test_camera_guard():
    """Test CameraGuard implementation."""
    print("Testing CameraGuard...")

    # Test 1: Camera disabled
    config = Settings()
    config.camera.enabled = False

    guard = CameraGuard(config)
    result = guard.check("test_job")
    print(f"  Camera disabled: {result.result.value} - {result.message}")
    assert result.result.value == "pass"

    # Test 2: Camera enabled but no URL
    config.camera.enabled = True
    config.camera.url = None

    result = guard.check("test_job")
    print(f"  Camera enabled, no URL: {result.result.value} - {result.message}")
    assert result.result.value == "soft_fail"

    # Test 3: Camera enabled with invalid URL
    config.camera.url = "http://invalid-url-that-does-not-exist.local"

    result = guard.check("test_job")
    print(f"  Camera with invalid URL: {result.result.value} - {result.message}")
    assert result.result.value == "soft_fail"

    # Test 4: Camera with device mode but no device
    config.camera.mode = "device"
    config.camera.device = "/dev/nonexistent-camera"

    result = guard.check("test_job")
    print(f"  Camera device not found: {result.result.value} - {result.message}")
    assert result.result.value == "soft_fail"

    print("  ✓ CameraGuard tests passed")


class TestPhysicalSetupGuard(unittest.TestCase):
    """Test PhysicalSetupGuard implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.paper = Mock()
        self.mock_config.paper.default_size = "A4"
        self.mock_config.multipen = Mock()
        self.mock_config.multipen.enabled = False
        self.mock_config.device = Mock()

        # Create temporary job directory for testing
        self.test_job_dir = Path(tempfile.mkdtemp())
        self.test_job_id = "test_job"

        # Create mock job file
        job_data = {
            "id": self.test_job_id,
            "name": "Test Job",
            "paper": "A4",
            "state": "READY",
        }
        job_file = self.test_job_dir / "job.json"
        job_file.write_text(json.dumps(job_data, indent=2))

        # Mock workspace to point to test directory and create jobs subdirectory
        jobs_dir = self.test_job_dir.parent / "jobs"
        jobs_dir.mkdir(exist_ok=True)
        # Move test job directory to jobs subdirectory
        job_dir = jobs_dir / self.test_job_id
        job_dir.mkdir(exist_ok=True)
        (self.test_job_dir / "job.json").rename(job_dir / "job.json")
        self.mock_config.workspace = str(self.test_job_dir.parent)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_job_dir, ignore_errors=True)

    def test_physical_setup_guard_pass_single_pen(self):
        """Test PhysicalSetupGuard with single pen setup."""
        from plotty.guards.system_guards import PhysicalSetupGuard

        guard = PhysicalSetupGuard(self.mock_config)
        result = guard.check(self.test_job_id)

        self.assertEqual(result.result, GuardResult.PASS)
        self.assertIn("validated", result.message.lower())
        self.assertTrue(result.details["paper_aligned"])
        self.assertTrue(result.details["pens_ready"])
        self.assertEqual(result.details["pen_count"], 1)
        self.assertFalse(result.details["has_multipen"])

    def test_physical_setup_guard_paper_size_mismatch(self):
        """Test PhysicalSetupGuard with paper size mismatch."""
        from plotty.guards.system_guards import PhysicalSetupGuard

        # Configure different paper size
        self.mock_config.paper.default_size = "A3"

        guard = PhysicalSetupGuard(self.mock_config)
        result = guard.check(self.test_job_id)

        self.assertEqual(result.result, GuardResult.FAIL)
        self.assertIn("Paper size mismatch", result.message)
        self.assertEqual(result.details["configured_paper"], "A3")
        self.assertEqual(result.details["required_paper"], "A4")
        self.assertFalse(result.details["paper_aligned"])

    def test_physical_setup_guard_multipen_not_enabled(self):
        """Test PhysicalSetupGuard when multipen required but not enabled."""
        from plotty.guards.system_guards import PhysicalSetupGuard

        # Use a different job ID for this test
        multipen_job_id = "multipen_test_job"

        # Create job directory in jobs folder
        jobs_dir = Path(self.mock_config.workspace) / "jobs"
        job_dir = jobs_dir / multipen_job_id
        job_dir.mkdir(exist_ok=True)

        # Create job requiring multipen
        job_data = {
            "id": multipen_job_id,
            "name": "Multipen Test Job",
            "paper": "A4",
            "state": "READY",
            "pen_mapping": {"pen1": "color1", "pen2": "color2"},
        }
        job_file = job_dir / "job.json"
        job_file.write_text(json.dumps(job_data, indent=2))

        guard = PhysicalSetupGuard(self.mock_config)
        result = guard.check(multipen_job_id)

        self.assertEqual(result.result, GuardResult.FAIL)
        self.assertIn("multipen is not enabled", result.message.lower())
        self.assertEqual(result.details["required_pen_count"], 2)
        self.assertFalse(result.details["multipen_enabled"])
        self.assertFalse(result.details["pens_ready"])


def run_all_tests():
    """Run all guard unit tests."""
    print("Running guard implementation unit tests...\n")

    try:
        test_paper_session_guard()
        print()
        test_pen_layer_guard()
        print()
        test_camera_guard()
        print()

        # Run PhysicalSetupGuard tests
        print("Testing PhysicalSetupGuard...")
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestPhysicalSetupGuard)
        test_runner = unittest.TextTestRunner(verbosity=0)
        result = test_runner.run(test_suite)

        if result.wasSuccessful():
            print("  ✓ PhysicalSetupGuard tests passed")
        else:
            print(
                f"  ❌ PhysicalSetupGuard tests failed: {len(result.failures)} failures"
            )
            for test, traceback in result.failures:
                print(f"    {test}: {traceback}")

        print("\n✅ All guard unit tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
