#!/usr/bin/env python3
"""Unit tests for new guard implementations."""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plotty.guards.job_guards import PaperSessionGuard, PenLayerGuard
from plotty.guards.system_guards import CameraGuard
from plotty.config import Settings, CameraCfg
from plotty.db import init_database, get_session
from plotty.models import Job, Paper, Pen, Layer, Base


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
                name="Test Paper",
                width_mm=210.0,
                height_mm=297.0,
                margin_mm=10.0
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
            print(f"  Job with available paper: {result.result.value} - {result.message}")
            assert result.result.value == "pass"
            
            # Test 4: Conflicting job
            conflicting_job = Job(
                id="conflicting_job", 
                state="QUEUED",  # Active state
                paper_id=paper.id
            )
            session.add(conflicting_job)
            session.commit()
            
            result = guard.check("job_with_paper")
            print(f"  Job with conflicting paper: {result.result.value} - {result.message}")
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
                name="Test Pen",
                width_mm=0.3,
                speed_cap=50.0,
                pressure=30,
                passes=1
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
                pen_id=None
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
                pen_id=pen.id
            )
            session.add(layer_with_pen)
            session.commit()
            
            result = guard.check("pen_test_job")
            print(f"  Mixed pen assignments: {result.result.value} - {result.message}")
            assert result.result.value == "soft_fail"  # Some layers compatible, some not
            
            # Test 4: All layers with valid pens
            layer_no_pen.pen_id = pen.id
            session.commit()
            
            result = guard.check("pen_test_job")
            print(f"  All layers compatible: {result.result.value} - {result.message}")
            assert result.result.value == "pass"
            
            # Test 5: Layer with non-existent pen
            session.query(Layer).filter(Layer.id == layer_with_pen.id).update({"pen_id": 999})
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


def run_all_tests():
    """Run all guard unit tests."""
    print("Running guard implementation unit tests...\n")
    
    try:
        test_paper_session_guard()
        print()
        test_pen_layer_guard()
        print()
        test_camera_guard()
        print("\n✅ All guard unit tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()