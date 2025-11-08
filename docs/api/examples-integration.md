# Examples and Integration

This section provides practical examples and integration patterns for working with ploTTY's APIs. These examples demonstrate common workflows, custom integrations, and advanced usage patterns.

## Quick Start Examples

### Basic Job Processing

```python
from pathlib import Path
from plotty.fsm import create_fsm, JobState
from plotty.plotting import MultiPenPlotter
from plotty.config import get_config

def simple_plot_job(job_id: str, svg_path: Path):
    """Simple job plotting workflow."""
    
    # Get configuration
    config = get_config()
    
    # Create FSM
    fsm = create_fsm(job_id, Path(config.workspace))
    
    # Process job through states
    if fsm.apply_optimizations(preset="default", digest=1):
        if fsm.queue_ready_job():
            if fsm.arm_job():
                # Start plotting
                fsm.transition_to(JobState.PLOTTING, "Starting plot")
                
                # Plot with MultiPenPlotter
                plotter = MultiPenPlotter(interactive=False)
                result = plotter.plot_with_axidraw_layers(svg_path)
                
                if result["success"]:
                    fsm.transition_to(JobState.COMPLETED, "Plot complete")
                    return True
                else:
                    fsm.transition_to(JobState.FAILED, f"Plot failed: {result['error']}")
    
    return False
```

### Batch Job Processing

```python
import glob
from pathlib import Path
from plotty.fsm import create_fsm
from plotty.config import get_config

def batch_process_svgs(input_pattern: str, preset: str = "default"):
    """Process multiple SVG files in batch."""
    
    config = get_config()
    workspace = Path(config.workspace)
    
    # Find all SVG files
    svg_files = glob.glob(input_pattern)
    
    processed = []
    failed = []
    
    for svg_file in svg_files:
        try:
            # Generate job ID from filename
            job_id = Path(svg_file).stem.lower().replace(" ", "_")
            
            # Create FSM
            fsm = create_fsm(job_id, workspace)
            
            # Process job
            if fsm.apply_optimizations(preset=preset, digest=1):
                if fsm.queue_ready_job():
                    processed.append(job_id)
                    print(f"✓ Processed {job_id}")
                else:
                    failed.append((job_id, "Queue failed"))
            else:
                failed.append((job_id, "Optimization failed"))
                
        except Exception as e:
            failed.append((job_id, str(e)))
    
    print(f"\nSummary: {len(processed)} processed, {len(failed)} failed")
    if failed:
        print("Failed jobs:")
        for job_id, error in failed:
            print(f"  {job_id}: {error}")
    
    return processed, failed
```

## CLI Integration Examples

### Custom CLI Commands

```python
import typer
from pathlib import Path
from plotty.fsm import create_fsm, JobState
from plotty.config import get_config

# Create custom CLI app
custom_app = typer.Typer(help="Custom ploTTY commands")

@custom_app.command()
def batch_plot(
    pattern: str = typer.Argument(..., help="File pattern (e.g., '*.svg')"),
    preset: str = typer.Option("default", "--preset", help="Optimization preset"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only")
):
    """Batch plot multiple files."""
    
    if dry_run:
        typer.echo(f"Would process files matching: {pattern}")
        typer.echo(f"Using preset: {preset}")
        return
    
    config = get_config()
    workspace = Path(config.workspace)
    
    # Process files
    from glob import glob
    files = glob(pattern)
    
    for file_path in files:
        job_id = Path(file_path).stem
        fsm = create_fsm(job_id, workspace)
        
        if fsm.apply_optimizations(preset=preset, digest=1):
            if fsm.queue_ready_job():
                typer.echo(f"✓ Queued {job_id}")
            else:
                typer.echo(f"✗ Failed to queue {job_id}")
        else:
            typer.echo(f"✗ Failed to optimize {job_id}")

if __name__ == "__main__":
    custom_app()
```

### ploTTY as Python Module

```python
#!/usr/bin/env python3
""" ploTTY integration script example """

import sys
import argparse
from pathlib import Path

# Add ploTTY to path if needed
sys.path.insert(0, '/path/to/plotty/src')

from plotty.fsm import create_fsm, JobState
from plotty.plotting import MultiPenPlotter
from plotty.config import load_config

def main():
    parser = argparse.ArgumentParser(description='ploTTY integration example')
    parser.add_argument('job_id', help='Job ID')
    parser.add_argument('svg_file', help='SVG file to plot')
    parser.add_argument('--preset', default='default', help='Optimization preset')
    parser.add_argument('--port', help='Device port')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Create FSM
    fsm = create_fsm(args.job_id, Path(config.workspace))
    
    # Process job
    if fsm.apply_optimizations(preset=args.preset, digest=1):
        if fsm.queue_ready_job():
            if fsm.arm_job():
                if not args.dry_run:
                    # Plot
                    plotter = MultiPenPlotter(port=args.port, interactive=False)
                    result = plotter.plot_with_axidraw_layers(Path(args.svg_file))
                    
                    if result["success"]:
                        fsm.transition_to(JobState.COMPLETED, "Plot complete")
                        print(f"✓ Job {args.job_id} completed successfully")
                    else:
                        fsm.transition_to(JobState.FAILED, f"Plot failed: {result['error']}")
                        print(f"✗ Job {args.job_id} failed: {result['error']}")
                else:
                    print(f"✓ Job {args.job_id} ready to plot (dry run)")
            else:
                print(f"✗ Failed to arm job {args.job_id}")
        else:
            print(f"✗ Failed to queue job {args.job_id}")
    else:
        print(f"✗ Failed to optimize job {args.job_id}")

if __name__ == "__main__":
    main()
```

## Database Integration Examples

### Custom Database Queries

```python
from plotty.db import get_session
from plotty.models import Job, Pen, Paper, JobStatistics
from sqlalchemy import func, and_
from datetime import datetime, timedelta

def get_job_statistics(days: int = 30):
    """Get job statistics for the last N days."""
    
    with get_session() as session:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Total jobs
        total_jobs = session.query(Job).filter(
            Job.created_at >= cutoff_date
        ).count()
        
        # Completed jobs
        completed_jobs = session.query(Job).filter(
            and_(
                Job.created_at >= cutoff_date,
                Job.state == "COMPLETED"
            )
        ).count()
        
        # Failed jobs
        failed_jobs = session.query(Job).filter(
            and_(
                Job.created_at >= cutoff_date,
                Job.state == "FAILED"
            )
        ).count()
        
        # Average plotting time
        avg_time = session.query(func.avg(JobStatistics.duration_seconds)).filter(
            and_(
                JobStatistics.timestamp >= cutoff_date,
                JobStatistics.event_type == "completed"
            )
        ).scalar() or 0
        
        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            "average_plotting_time": avg_time
        }

def get_pen_usage():
    """Get pen usage statistics."""
    
    with get_session() as session:
        # Query pen usage from layer statistics
        pen_usage = session.query(
            Pen.name,
            func.sum(LayerStatistics.distance_plotted_mm).label('total_distance'),
            func.count(LayerStatistics.id).label('layer_count')
        ).join(
            LayerStatistics, Pen.id == LayerStatistics.pen_id
        ).group_by(Pen.name).all()
        
        return [
            {
                "pen_name": name,
                "total_distance": float(distance),
                "layer_count": count
            }
            for name, distance, count in pen_usage
        ]

def get_queue_status():
    """Get current job queue status."""
    
    with get_session() as session:
        # Jobs in queue by state
        queue_status = session.query(
            Job.state,
            func.count(Job.id).label('count')
        ).filter(
            Job.state.in_(['QUEUED', 'READY', 'ARMED', 'PLOTTING'])
        ).group_by(Job.state).all()
        
        return {state: count for state, count in queue_status}
```

### Custom Model Operations

```python
from plotty.db import get_session
from plotty.models import Pen, Paper, Job
from sqlalchemy.exc import IntegrityError

def create_custom_pen(name: str, width_mm: float, color: str, **kwargs):
    """Create a custom pen with validation."""
    
    with get_session() as session:
        try:
            # Check if pen already exists
            existing = session.query(Pen).filter(Pen.name == name).first()
            if existing:
                raise ValueError(f"Pen '{name}' already exists")
            
            # Create new pen
            pen = Pen(
                name=name,
                width_mm=width_mm,
                color_hex=color,
                **kwargs
            )
            
            session.add(pen)
            session.commit()
            
            print(f"✓ Created pen '{name}'")
            return pen
            
        except IntegrityError as e:
            session.rollback()
            raise ValueError(f"Invalid pen data: {e}")
        except Exception as e:
            session.rollback()
            raise

def update_job_metadata(job_id: str, metadata: dict):
    """Update job metadata."""
    
    with get_session() as session:
        job = session.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job '{job_id}' not found")
        
        # Update metadata JSON field
        if job.metrics_json:
            job.metrics_json.update(metadata)
        else:
            job.metrics_json = metadata
        
        session.commit()
        print(f"✓ Updated metadata for job '{job_id}'")
```

## Web Integration Examples

### Flask Web API

```python
from flask import Flask, request, jsonify
from pathlib import Path
from plotty.fsm import create_fsm, JobState
from plotty.config import get_config
from plotty.db import get_session
from plotty.models import Job

app = Flask(__name__)

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs."""
    
    with get_session() as session:
        jobs = session.query(Job).all()
        return jsonify([
            {
                "id": job.id,
                "name": job.name,
                "state": job.state,
                "created_at": job.created_at.isoformat()
            }
            for job in jobs
        ])

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id: str):
    """Get job details."""
    
    with get_session() as session:
        job = session.query(Job).filter(Job.id == job_id).first()
        if not job:
            return jsonify({"error": "Job not found"}), 404
        
        return jsonify({
            "id": job.id,
            "name": job.name,
            "state": job.state,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
            "metrics": job.metrics_json
        })

@app.route('/api/jobs/<job_id>/plot', methods=['POST'])
def plot_job(job_id: str):
    """Start plotting a job."""
    
    try:
        config = get_config()
        fsm = create_fsm(job_id, Path(config.workspace))
        
        if fsm.current_state != JobState.READY:
            return jsonify({"error": "Job not ready for plotting"}), 400
        
        if fsm.arm_job():
            fsm.transition_to(JobState.PLOTTING, "API started plot")
            return jsonify({"message": "Plotting started"})
        else:
            return jsonify({"error": "Failed to arm job"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new job."""
    
    data = request.get_json()
    
    try:
        config = get_config()
        fsm = create_fsm(data['job_id'], Path(config.workspace))
        
        # Process job creation logic here
        # This is a simplified example
        
        return jsonify({"message": "Job created", "job_id": data['job_id']}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI Web Service

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path

from plotty.fsm import create_fsm, JobState
from plotty.config import get_config
from plotty.db import get_session
from plotty.models import Job

app = FastAPI(title="ploTTY API", version="1.0.0")

class JobCreate(BaseModel):
    job_id: str
    name: str
    svg_path: str
    preset: str = "default"

class JobResponse(BaseModel):
    id: str
    name: str
    state: str
    created_at: str
    updated_at: Optional[str] = None

@app.get("/api/jobs", response_model=List[JobResponse])
async def list_jobs():
    """List all jobs."""
    
    with get_session() as session:
        jobs = session.query(Job).all()
        return [
            JobResponse(
                id=job.id,
                name=job.name,
                state=job.state,
                created_at=job.created_at.isoformat(),
                updated_at=job.updated_at.isoformat() if job.updated_at else None
            )
            for job in jobs
        ]

@app.post("/api/jobs/{job_id}/plot")
async def plot_job(job_id: str, preset: str = "default"):
    """Start plotting a job."""
    
    try:
        config = get_config()
        fsm = create_fsm(job_id, Path(config.workspace))
        
        if fsm.current_state != JobState.READY:
            raise HTTPException(status_code=400, detail="Job not ready for plotting")
        
        if fsm.arm_job():
            fsm.transition_to(JobState.PLOTTING, "API started plot")
            return {"message": "Plotting started", "job_id": job_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to arm job")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """Get job status."""
    
    with get_session() as session:
        job = session.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "id": job.id,
            "name": job.name,
            "state": job.state,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            "metrics": job.metrics_json
        }
```

## Automation Examples

### File Watcher Integration

```python
import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from plotty.fsm import create_fsm
from plotty.config import get_config

class PlotFileHandler(FileSystemEventHandler):
    """Handle new SVG files for automatic plotting."""
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.svg'):
            print(f"New SVG file detected: {event.src_path}")
            self.process_file(Path(event.src_path))
    
    def process_file(self, file_path: Path):
        """Process new SVG file."""
        
        try:
            # Generate job ID from filename
            job_id = file_path.stem.lower().replace(" ", "_")
            
            # Get configuration
            config = get_config()
            
            # Create FSM
            fsm = create_fsm(job_id, Path(config.workspace))
            
            # Process job
            if fsm.apply_optimizations(preset="default", digest=1):
                if fsm.queue_ready_job():
                    print(f"✓ Automatically queued job: {job_id}")
                else:
                    print(f"✗ Failed to queue job: {job_id}")
            else:
                print(f"✗ Failed to optimize job: {job_id}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

def start_file_watcher(watch_directory: str):
    """Start file watcher for automatic job processing."""
    
    event_handler = PlotFileHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

# Usage
if __name__ == "__main__":
    start_file_watcher("/path/to/svg/files")
```

### Scheduled Job Processing

```python
import schedule
import time
from pathlib import Path
from plotty.fsm import create_fsm, JobState
from plotty.plotting import MultiPenPlotter
from plotty.config import get_config

def process_queued_jobs():
    """Process all queued jobs."""
    
    config = get_config()
    workspace = Path(config.workspace)
    
    # Get queued jobs (this would need to be implemented based on your storage)
    queued_jobs = get_queued_jobs(workspace)  # Custom function
    
    for job_id in queued_jobs:
        try:
            fsm = create_fsm(job_id, workspace)
            
            if fsm.current_state == JobState.QUEUED:
                if fsm.arm_job():
                    # Start plotting
                    fsm.transition_to(JobState.PLOTTING, "Scheduled plot")
                    
                    # Plot job
                    plotter = MultiPenPlotter(interactive=False)
                    svg_path = workspace / "jobs" / job_id / "multipen.svg"
                    
                    if svg_path.exists():
                        result = plotter.plot_with_axidraw_layers(svg_path)
                        
                        if result["success"]:
                            fsm.transition_to(JobState.COMPLETED, "Scheduled plot complete")
                            print(f"✓ Completed job: {job_id}")
                        else:
                            fsm.transition_to(JobState.FAILED, f"Scheduled plot failed: {result['error']}")
                            print(f"✗ Failed job: {job_id}")
                    else:
                        print(f"✗ SVG not found for job: {job_id}")
                        
        except Exception as e:
            print(f"Error processing job {job_id}: {e}")

# Schedule processing every 5 minutes
schedule.every(5).minutes.do(process_queued_jobs)

# Schedule daily cleanup
schedule.every().day.at("02:00").do(cleanup_old_jobs)

print("Starting scheduled job processor...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Testing Examples

### Unit Testing with ploTTY

```python
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from plotty.fsm import create_fsm, JobState
from plotty.testing import TestEnvironment, create_test_job

class TestPlottingWorkflow(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.env = TestEnvironment()
        self.test_svg = "<svg><rect x='10' y='10' width='100' height='100'/></svg>"
    
    def test_job_creation(self):
        """Test job creation and initial state."""
        
        # Create test job
        job_id = create_test_job(
            self.env.workspace,
            self.test_svg,
            name="test_job"
        )
        
        # Create FSM
        fsm = create_fsm(job_id, self.env.workspace)
        
        # Check initial state
        self.assertEqual(fsm.current_state, JobState.NEW)
        
        # Check job data
        job_data = fsm.get_job_data()
        self.assertEqual(job_data['id'], job_id)
        self.assertEqual(job_data['name'], 'test_job')
    
    def test_optimization_workflow(self):
        """Test optimization workflow."""
        
        # Create test job
        job_id = create_test_job(
            self.env.workspace,
            self.test_svg,
            name="test_optimization"
        )
        
        # Create FSM
        fsm = create_fsm(job_id, self.env.workspace)
        
        # Apply optimizations
        success = fsm.apply_optimizations(preset="fast", digest=1)
        self.assertTrue(success)
        
        # Check state
        self.assertEqual(fsm.current_state, JobState.READY)
        
        # Check job data
        job_data = fsm.get_job_data()
        self.assertEqual(job_data['state'], JobState.READY.value)
    
    def test_state_transitions(self):
        """Test state transitions."""
        
        # Create test job
        job_id = create_test_job(
            self.env.workspace,
            self.test_svg,
            name="test_transitions"
        )
        
        # Create FSM
        fsm = create_fsm(job_id, self.env.workspace)
        
        # Test valid transitions
        self.assertTrue(fsm.can_transition_to(JobState.ANALYZED))
        self.assertFalse(fsm.can_transition_to(JobState.COMPLETED))
        
        # Transition to ANALYZED
        success = fsm.transition_to(JobState.ANALYZED, "Test transition")
        self.assertTrue(success)
        self.assertEqual(fsm.current_state, JobState.ANALYZED)
        
        # Test invalid transition
        success = fsm.transition_to(JobState.NEW, "Invalid transition")
        self.assertFalse(success)
        self.assertEqual(fsm.current_state, JobState.ANALYZED)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
import pytest
from pathlib import Path
from plotty.fsm import create_fsm, JobState
from plotty.plotting import MultiPenPlotter
from plotty.testing import TestEnvironment, create_test_job

@pytest.fixture
def test_env():
    """Create test environment."""
    return TestEnvironment()

@pytest.fixture
def sample_job(test_env):
    """Create sample job for testing."""
    svg_content = """
    <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="10" width="80" height="80" fill="none" stroke="black"/>
        <circle cx="50" cy="50" r="20" fill="none" stroke="red"/>
    </svg>
    """
    
    job_id = create_test_job(
        test_env.workspace,
        svg_content,
        name="integration_test"
    )
    
    return job_id

def test_complete_workflow(test_env, sample_job):
    """Test complete plotting workflow."""
    
    # Create FSM
    fsm = create_fsm(sample_job, test_env.workspace)
    
    # Process through states
    assert fsm.current_state == JobState.NEW
    
    # Optimize
    assert fsm.apply_optimizations(preset="default", digest=1)
    assert fsm.current_state == JobState.READY
    
    # Queue
    assert fsm.queue_ready_job()
    assert fsm.current_state == JobState.QUEUED
    
    # Arm
    assert fsm.arm_job()
    assert fsm.current_state == JobState.ARMED
    
    # Start plotting (mock)
    assert fsm.transition_to(JobState.PLOTTING, "Test plot")
    assert fsm.current_state == JobState.PLOTTING
    
    # Complete
    assert fsm.transition_to(JobState.COMPLETED, "Test complete")
    assert fsm.current_state == JobState.COMPLETED

def test_error_handling(test_env, sample_job):
    """Test error handling in workflow."""
    
    fsm = create_fsm(sample_job, test_env.workspace)
    
    # Try invalid transition
    success = fsm.transition_to(JobState.COMPLETED, "Invalid transition")
    assert not success
    assert fsm.current_state == JobState.NEW
    
    # Check error
    error = fsm.get_last_error()
    assert error is not None
```

These examples demonstrate various ways to integrate with ploTTY's APIs, from simple scripts to complex web applications and automated workflows. The key is understanding the FSM-based job lifecycle and using the appropriate APIs for your use case.