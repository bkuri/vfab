# Database Models

vfab uses SQLAlchemy ORM with a well-defined database schema for managing plotting resources, jobs, and statistics. The models are defined in `src/vfab/models.py` and managed through Alembic migrations.

## Core Models

### Device

Represents a plotter device configuration.

```python
class Device(Base):
    """Plotter device model."""
    
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True)
    kind = Column(String, nullable=False)          # Device type (e.g., "axidraw")
    name = Column(String)                          # Human-readable name
    port = Column(String)                          # Device port/path
    firmware = Column(String)                      # Firmware version
    defaults_json = Column(JSON)                   # Default settings
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

**Fields:**
- `id`: Primary key
- `kind`: Device type (required)
- `name`: Optional device name
- `port`: Device connection port
- `firmware`: Firmware version string
- `defaults_json`: JSON-encoded default settings
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Pen

Represents different plotting tools/pen configurations.

```python
class Pen(Base):
    """Pen model for different plotting tools."""
    
    __tablename__ = "pens"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # Unique pen name
    width_mm = Column(Float)                             # Pen width in mm
    speed_cap = Column(Float)                            # Maximum speed
    pressure = Column(Integer)                           # Pressure setting (0-100)
    passes = Column(Integer)                             # Number of passes
    color_hex = Column(String)                           # Color in hex format
    
    # Relationships
    layers = relationship("Layer", back_populates="pen")
```

**Fields:**
- `id`: Primary key
- `name`: Unique pen identifier (required)
- `width_mm`: Pen tip width in millimeters
- `speed_cap`: Maximum plotting speed
- `pressure`: Pressure setting (0-100)
- `passes`: Number of passes for this pen
- `color_hex`: Color representation in hex format

**Relationships:**
- `layers`: One-to-many relationship with Layer model

### Paper

Represents paper size and configuration.

```python
class Paper(Base):
    """Paper size model."""
    
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # Unique paper name
    width_mm = Column(Float, nullable=False)             # Width in mm
    height_mm = Column(Float, nullable=False)            # Height in mm
    margin_mm = Column(Float)                            # Margin in mm
    orientation = Column(String)                         # Orientation (portrait/landscape)
    
    # Relationships
    jobs = relationship("Job", back_populates="paper")
```

**Fields:**
- `id`: Primary key
- `name`: Unique paper identifier (required)
- `width_mm`: Paper width in millimeters (required)
- `height_mm`: Paper height in millimeters (required)
- `margin_mm`: Default margin in millimeters
- `orientation`: Paper orientation ("portrait" or "landscape")

**Relationships:**
- `jobs`: One-to-many relationship with Job model

### Job

Represents a plotting job with its metadata and state.

```python
class Job(Base):
    """Plotting job model."""
    
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)               # Job ID (string)
    name = Column(String)                                # Human-readable name
    src_path = Column(String)                            # Source file path
    opt_path = Column(String)                            # Optimized file path
    paper_id = Column(Integer, ForeignKey("papers.id"))  # Foreign key to Paper
    state = Column(String, nullable=False)               # Job state
    timings_json = Column(JSON)                          # Timing information
    metrics_json = Column(JSON)                          # Performance metrics
    media_json = Column(JSON)                            # Media information
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    paper = relationship("Paper", back_populates="jobs")
    layers = relationship("Layer", back_populates="job")
```

**Fields:**
- `id`: Job identifier (string, primary key)
- `name`: Human-readable job name
- `src_path`: Path to source SVG/PLOB file
- `opt_path`: Path to optimized file
- `paper_id`: Foreign key to Paper model
- `state`: Current job state (see Job States section)
- `timings_json`: JSON-encoded timing data
- `metrics_json`: JSON-encoded performance metrics
- `media_json`: JSON-encoded media information
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Relationships:**
- `paper`: Many-to-one relationship with Paper model
- `layers`: One-to-many relationship with Layer model

### Layer

Represents individual layers within a multi-pen job.

```python
class Layer(Base):
    """Layer model for multi-pen plotting."""
    
    __tablename__ = "layers"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)  # Foreign key to Job
    layer_name = Column(String, nullable=False)                     # Layer name
    order_index = Column(Integer, nullable=False)                    # Plotting order
    pen_id = Column(Integer, ForeignKey("pens.id"))                  # Foreign key to Pen
    stats_json = Column(JSON)                                        # Layer statistics
    planned = Column(Boolean, default=False)                        # Planning status
    
    # Relationships
    job = relationship("Job", back_populates="layers")
    pen = relationship("Pen", back_populates="layers")
```

**Fields:**
- `id`: Primary key
- `job_id`: Foreign key to Job model (required)
- `layer_name`: Name/identifier of the layer (required)
- `order_index`: Plotting order index (required)
- `pen_id`: Foreign key to Pen model
- `stats_json`: JSON-encoded layer statistics
- `planned`: Whether layer has been planned

**Relationships:**
- `job`: Many-to-one relationship with Job model
- `pen`: Many-to-one relationship with Pen model

## Statistics Models

### StatisticsConfig

Configuration for statistics collection.

```python
class StatisticsConfig(Base):
    """Statistics configuration model."""
    
    __tablename__ = "statistics_config"
    
    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, default=False, nullable=False)      # Statistics enabled
    collection_level = Column(String, default="basic", nullable=False)  # Collection level
    retention_days = Column(Integer, default=365)                  # Data retention period
    auto_cleanup = Column(Boolean, default=True)                   # Auto cleanup old data
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### JobStatistics

Statistics collected for individual jobs.

```python
class JobStatistics(Base):
    """Job statistics model."""
    
    __tablename__ = "job_statistics"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)  # Foreign key to Job
    collection_level = Column(String, nullable=False)               # Data collection level
    event_type = Column(String, nullable=False)                     # Event type
    timestamp = Column(DateTime, default=func.now(), nullable=False)  # Event timestamp
    duration_seconds = Column(Float)                                # Event duration
    pen_changes = Column(Integer, default=0)                        # Number of pen changes
    distance_plotted_mm = Column(Float, default=0.0)                 # Distance plotted
    distance_travel_mm = Column(Float, default=0.0)                 # Total travel distance
    pen_down_time_seconds = Column(Float, default=0.0)              # Pen down time
    pen_up_time_seconds = Column(Float, default=0.0)                 # Pen up time
    layers_completed = Column(Integer, default=0)                   # Layers completed
    total_layers = Column(Integer, default=0)                       # Total layers
    metadata_json = Column(JSON)                                    # Additional metadata
    
    # Relationships
    job = relationship("Job")
```

### LayerStatistics

Statistics collected for individual layers.

```python
class LayerStatistics(Base):
    """Layer statistics model."""
    
    __tablename__ = "layer_statistics"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)   # Foreign key to Job
    layer_id = Column(Integer, ForeignKey("layers.id"), nullable=False)  # Foreign key to Layer
    pen_id = Column(Integer, ForeignKey("pens.id"))                  # Foreign key to Pen
    timestamp = Column(DateTime, default=func.now(), nullable=False)  # Timestamp
    duration_seconds = Column(Float)                                 # Duration
    distance_plotted_mm = Column(Float, default=0.0)                 # Distance plotted
    distance_travel_mm = Column(Float, default=0.0)                  # Travel distance
    pen_down_time_seconds = Column(Float, default=0.0)               # Pen down time
    pen_up_time_seconds = Column(Float, default=0.0)                 # Pen up time
    path_count = Column(Integer, default=0)                         # Number of paths
    point_count = Column(Integer, default=0)                         # Number of points
    metadata_json = Column(JSON)                                      # Additional metadata
    
    # Relationships
    job = relationship("Job")
    layer = relationship("Layer")
    pen = relationship("Pen")
```

### SystemStatistics

System-wide statistics and summaries.

```python
class SystemStatistics(Base):
    """System statistics model."""
    
    __tablename__ = "system_statistics"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)  # Timestamp
    stat_type = Column(String, nullable=False)                       # Statistics type
    total_jobs = Column(Integer, default=0)                           # Total jobs
    completed_jobs = Column(Integer, default=0)                      # Completed jobs
    failed_jobs = Column(Integer, default=0)                          # Failed jobs
    total_plotting_time_seconds = Column(Float, default=0.0)          # Total plotting time
    total_distance_plotted_mm = Column(Float, default=0.0)            # Total distance plotted
    total_pen_changes = Column(Integer, default=0)                    # Total pen changes
    avg_job_duration_seconds = Column(Float)                         # Average job duration
    metadata_json = Column(JSON)                                      # Additional metadata
```

### PerformanceMetrics

Performance metrics for analysis.

```python
class PerformanceMetrics(Base):
    """Performance metrics model."""
    
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"))                   # Foreign key to Job
    timestamp = Column(DateTime, default=func.now(), nullable=False)  # Timestamp
    metric_type = Column(String, nullable=False)                     # Metric type
    metric_value = Column(Float, nullable=False)                     # Metric value
    unit = Column(String)                                             # Unit of measurement
    context_json = Column(JSON)                                       # Context information
    
    # Relationships
    job = relationship("Job")
```

## Database Schema Relationships

```
Device (1) -----> (0..*) Job
Paper (1) ------> (0..*) Job
Pen (1) ---------> (0..*) Layer
Job (1) ---------> (0..*) Layer
Job (1) ---------> (0..*) JobStatistics
Job (1) ---------> (0..*) LayerStatistics
Job (1) ---------> (0..*) PerformanceMetrics
Layer (1) ------> (0..*) LayerStatistics
Pen (1) --------> (0..*) LayerStatistics
```

## Job States

Jobs progress through the following states (defined in `JobState` enum):

- `NEW`: Job created, not yet processed
- `QUEUED`: Job added to processing queue
- `ANALYZED`: Job analysis completed
- `OPTIMIZED`: Job optimization completed
- `READY`: Job ready for plotting
- `ARMED`: Pre-flight checks completed
- `PLOTTING`: Currently being plotted
- `PAUSED`: Plotting paused
- `COMPLETED`: Plotting finished successfully
- `ABORTED`: Plotting aborted by user
- `FAILED`: Plotting failed due to error

## Database Operations

### Session Management

```python
from vfab.db import get_session

# Using context manager
with get_session() as session:
    # Query operations
    pens = session.query(Pen).all()
    
    # Create new record
    new_pen = Pen(name="0.5mm red", width_mm=0.5, color_hex="#FF0000")
    session.add(new_pen)
    session.commit()
```

### Common Queries

```python
# Get all jobs in specific state
queued_jobs = session.query(Job).filter(Job.state == "QUEUED").all()

# Get job with its layers and pens
job_with_layers = session.query(Job).options(
    joinedload(Job.layers).joinedload(Layer.pen)
).filter(Job.id == job_id).first()

# Get statistics for a job
job_stats = session.query(JobStatistics).filter(
    JobStatistics.job_id == job_id
).order_by(JobStatistics.timestamp.desc()).all()
```

### Database Migrations

Database schema is managed through Alembic migrations:

```bash
# Create new migration
uv run alembic revision --autogenerate -m "Add new feature"

# Apply migrations
uv run alembic upgrade head

# Downgrade migrations
uv run alembic downgrade -1
```

## JSON Field Schemas

### timings_json
```json
{
    "analysis_time": 12.5,
    "optimization_time": 8.3,
    "plotting_time": 1800.0,
    "total_time": 1820.8
}
```

### metrics_json
```json
{
    "distance_plotted": 15000.0,
    "distance_travel": 25000.0,
    "pen_changes": 3,
    "layer_count": 5,
    "path_count": 127,
    "point_count": 15420
}
```

### media_json
```json
{
    "file_size": 1048576,
    "file_type": "svg",
    "compression_ratio": 0.75,
    "layer_info": {
        "layer1": {"pen": "0.3mm black", "paths": 45},
        "layer2": {"pen": "0.5mm red", "paths": 82}
    }
}
```

## Database Configuration

The database connection is configured through the `DatabaseCfg` model:

```python
class DatabaseCfg(BaseModel):
    url: str = "sqlite:///path/to/vfab.db"
    echo: bool = False  # Enable SQLAlchemy query logging
```

Default database is SQLite, but PostgreSQL is also supported:

```yaml
# config/config.yaml
database:
  url: "postgresql://user:password@localhost/vfab"
  echo: false
```