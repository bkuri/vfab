# Driver Development Guide

This guide provides comprehensive instructions for adding new hardware drivers to vfab. Whether you're adding support for a new plotter, camera system, or other hardware device, this guide will walk you through the entire process.

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Driver Types](#3-driver-types)
4. [Step-by-Step Guide](#4-step-by-step-guide)
5. [Code Examples](#5-code-examples)
6. [Testing Guidelines](#6-testing-guidelines)
7. [Configuration Integration](#7-configuration-integration)
8. [Common Patterns](#8-common-patterns)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Overview

The vfab driver system is designed to be extensible and modular. Drivers are organized into several key components:

### Core Components

- **Driver Modules** (`src/vfab/drivers/`) - Hardware-specific implementations
- **Detection System** (`src/vfab/detection.py`) - Hardware discovery and validation
- **CLI Integration** (`src/vfab/cli/driver/`) - Command-line interface for driver management
- **Configuration** (`src/vfab/config.py`) - Driver-specific settings and options

### Driver Architecture Flow

```
User Command → CLI Driver → Driver Module → Hardware Detection → Device Manager
     ↓                ↓                ↓                    ↓              ↓
vfab driver → install/info → is_available() → detect_devices() → create_manager()
```

---

## 2. Prerequisites

### Development Environment

- **Python**: 3.11+ with `from __future__ import annotations`
- **Dependencies**: vfab development environment (`uv pip install -e ".[dev]"`)
- **Tools**: `ruff` for linting, `black` for formatting, `pytest` for testing

### Required Knowledge

- **Typer**: For CLI command integration
- **Pydantic**: For configuration models
- **SQLAlchemy**: For database integration (if needed)
- **Hardware Protocols**: USB, serial, network communication as needed

### Development Commands

```bash
# Install development environment
uv pip install -e ".[dev]"

# Run linting
uvx ruff check src/vfab/drivers/

# Format code
uvx black src/vfab/drivers/

# Run tests
uv run pytest tests/test_driver_*.py -q
```

---

## 3. Driver Types

vfab supports several types of drivers:

### Hardware Drivers

**Plotter Drivers**: Physical plotting devices
- Example: AxiDraw (`axidraw.py`)
- Responsibilities: Device control, movement, pen management

**Camera Drivers**: Imaging and monitoring devices
- Example: USB cameras, IP cameras
- Responsibilities: Image capture, streaming, motion detection

**Sensor Drivers**: Environmental and position sensors
- Example: Limit switches, encoders
- Responsibilities: State monitoring, position feedback

### System Drivers

**Database Drivers**: Data persistence and storage
- Examples: SQLite, PostgreSQL
- Responsibilities: Connection management, queries, migrations

---

## 4. Step-by-Step Guide

### 4.1 Create Driver Module

Create a new file in `src/vfab/drivers/`:

```python
"""
New hardware driver for vfab.

This module provides support for [Device Name] hardware.
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from pathlib import Path

# Import availability flag
_AVAILABLE = False
_IMPORT_ERROR = "Driver not available. Install with: vfab driver install [driver_name]"

try:
    # Import hardware-specific libraries here
    import hardware_library
    _AVAILABLE = True
except ImportError:
    hardware_library = None
    _IMPORT_ERROR = "hardware_library not found. Install with: pip install hardware_library"
```

### 4.2 Implement Required Methods

Every driver must implement these core functions:

```python
def is_[driver_name]_available() -> bool:
    """Check if driver dependencies are available.
    
    Returns:
        True if driver can be used, False otherwise
    """
    return _AVAILABLE

def get_[driver_name]_install_instructions() -> str:
    """Get installation instructions for missing dependencies.
    
    Returns:
        String with installation instructions
    """
    return _IMPORT_ERROR

def create_[driver_name]_manager(
    port: Optional[str] = None,
    **kwargs
) -> [DriverName]Manager:
    """Factory function to create driver manager.
    
    Args:
        port: Device port or connection identifier
        **kwargs: Additional driver-specific options
        
    Returns:
        Manager instance for the driver
        
    Raises:
        ImportError: If driver dependencies are not available
    """
    if not _AVAILABLE:
        raise ImportError(_IMPORT_ERROR)
    
    return [DriverName]Manager(port=port, **kwargs)
```

### 4.3 Create Manager Class

Implement the device management class:

```python
class [DriverName]Manager:
    """Manages [Device Name] hardware operations."""
    
    def __init__(self, port: Optional[str] = None, **options):
        """Initialize manager.
        
        Args:
            port: Device connection identifier
            **options: Driver-specific configuration
        """
        if not _AVAILABLE:
            raise ImportError(_IMPORT_ERROR)
            
        self.port = port
        self.connected = False
        # Initialize driver-specific state
        
    def connect(self) -> bool:
        """Connect to hardware device.
        
        Returns:
            True if connection successful, False otherwise
        """
        # Implement connection logic
        pass
        
    def disconnect(self) -> None:
        """Disconnect from hardware device."""
        # Implement disconnection logic
        pass
        
    def test_connection(self) -> Dict[str, Any]:
        """Test device connectivity and functionality.
        
        Returns:
            Dictionary with test results
        """
        # Implement connection testing
        pass
```

### 4.4 Add Hardware Detection

Extend `DeviceDetector` class in `src/vfab/detection.py`:

```python
def detect_[driver_name]_devices(self) -> Dict[str, Any]:
    """Detect [Device Name] hardware devices.
    
    Returns:
        Dictionary with device detection results:
        - count: Number of devices found
        - installed: Whether driver is installed
        - device_id: USB/Network device identifier
        - device_name: Human readable device name
        - accessible: Whether devices are accessible
        - devices: List of detailed device information
    """
    result = {
        "count": 0,
        "installed": self._check_[driver_name]_installed(),
        "device_id": "vendor:product",
        "device_name": "[Device Name] compatible device",
        "accessible": False,
        "devices": []
    }
    
    # Implement device detection logic
    # USB detection, network scanning, etc.
    
    return result

def _check_[driver_name]_installed(self) -> bool:
    """Check if [driver name] module is available."""
    try:
        import importlib.util
        spec = importlib.util.find_spec("hardware_library")
        return spec is not None
    except ImportError:
        return False
```

### 4.5 Integrate with CLI Commands

Update driver CLI commands in `src/vfab/cli/driver/`:

#### Install Command (`install.py`)

```python
# Add to driver validation
if driver.lower() not in ["axidraw", "[driver_name]"]:
    supported = ["axidraw", "[driver_name]"]
    raise typer.BadParameter(
        f"Unsupported driver: {driver}. Supported: {', '.join(supported)}"
    )

# Add installation logic
elif driver.lower() == "[driver_name]":
    from ...drivers.[driver_name] import is_[driver_name]_available
    
    if not is_[driver_name]_available() or force:
        show_status(f"Installing {driver} support...", "info")
        # Install driver dependencies
        cmd = [sys.executable, "-m", "uv", "pip", "install", "[driver_package]"]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
```

#### List Command (`list.py`)

```python
# Add driver to status display
from ...drivers.[driver_name] import is_[driver_name]_available

[driver_name]_available = is_[driver_name]_available()
# Add to results table
table.add_row("[Device Name]", status, hardware, install_cmd)
```

#### Info Command (`info.py`)

```python
# Add driver information display
elif driver.lower() == "[driver_name]":
    from ...drivers.[driver_name] import (
        is_[driver_name]_available,
        get_[driver_name]_install_instructions,
        create_[driver_name]_manager
    )
```

#### Test Command (`test.py`)

```python
# Add driver testing
elif driver.lower() == "[driver_name]":
    from ...drivers.[driver_name] import (
        is_[driver_name]_available,
        create_[driver_name]_manager
    )
```

### 4.6 Add Configuration Support

Update configuration schema in `src/vfab/config.py`:

```python
# Add to device configuration model
class DeviceConfig(BaseModel):
    # Existing fields...
    [driver_name]_port: Optional[str] = None
    [driver_name]_timeout: int = 5
    [driver_name]_option: str = "default"
```

### 4.7 Update Driver Exports

Update `src/vfab/drivers/__init__.py`:

```python
from .[driver_name] import (
    [DriverName]Manager,
    create_[driver_name]_manager,
    is_[driver_name]_available,
    get_[driver_name]_install_instructions
)

__all__ = [
    "AxiDrawManager", "create_manager", "is_axidraw_available",
    "[DriverName]Manager", "create_[driver_name]_manager", "is_[driver_name]_available"
]
```

### 4.8 Write Tests

Create comprehensive tests in `tests/test_driver_[driver_name].py`:

```python
"""Tests for [driver name] driver."""

import pytest
from unittest.mock import Mock, patch
from vfab.drivers.[driver_name] import (
    is_[driver_name]_available,
    create_[driver_name]_manager,
    [DriverName]Manager
)

class Test[DriverName]Driver:
    """Test suite for [driver name] driver."""
    
    def test_availability_check(self):
        """Test driver availability detection."""
        result = is_[driver_name]_available()
        assert isinstance(result, bool)
    
    def test_manager_creation(self):
        """Test manager factory function."""
        if is_[driver_name]_available():
            manager = create_[driver_name]_manager()
            assert isinstance(manager, [DriverName]Manager)
        else:
            with pytest.raises(ImportError):
                create_[driver_name]_manager()
    
    def test_connection_workflow(self):
        """Test connection and disconnection."""
        if not is_[driver_name]_available():
            pytest.skip("Driver not available")
            
        manager = create_[driver_name]_manager()
        
        # Test connection
        result = manager.connect()
        assert isinstance(result, bool)
        
        if result:
            # Test disconnection
            manager.disconnect()
            assert not manager.connected
```

---

## 5. Code Examples

### Complete Example: Simple Plotter Driver

```python
"""
Simple plotter driver example.

This demonstrates the basic structure for adding a new plotter driver.
"""

from __future__ import annotations
from typing import Optional, Dict, Any
import time

# Driver availability
_AVAILABLE = False
_IMPORT_ERROR = "simple_plotter not found. Install with: pip install simple-plotter"

try:
    import simple_plotter
    _AVAILABLE = True
except ImportError:
    simple_plotter = None

def is_simple_plotter_available() -> bool:
    """Check if simple plotter driver is available."""
    return _AVAILABLE

def get_simple_plotter_install_instructions() -> str:
    """Get installation instructions."""
    return _IMPORT_ERROR

def create_simple_plotter_manager(
    port: Optional[str] = None,
    speed: int = 1000
) -> SimplePlotterManager:
    """Create simple plotter manager."""
    if not _AVAILABLE:
        raise ImportError(_IMPORT_ERROR)
    
    return SimplePlotterManager(port=port, speed=speed)

class SimplePlotterManager:
    """Manages simple plotter operations."""
    
    def __init__(self, port: Optional[str] = None, speed: int = 1000):
        self.port = port
        self.speed = speed
        self.connected = False
        self.plotter = None
        
    def connect(self) -> bool:
        """Connect to plotter."""
        try:
            self.plotter = simple_plotter.Plotter(port=self.port)
            self.plotter.connect()
            self.connected = True
            return True
        except Exception:
            return False
    
    def disconnect(self) -> None:
        """Disconnect from plotter."""
        if self.connected and self.plotter:
            self.plotter.disconnect()
            self.connected = False
    
    def move_to(self, x: float, y: float) -> None:
        """Move to position."""
        if not self.connected:
            raise RuntimeError("Not connected to plotter")
        self.plotter.move_to(x, y, speed=self.speed)
    
    def pen_up(self) -> None:
        """Raise pen."""
        if not self.connected:
            raise RuntimeError("Not connected to plotter")
        self.plotter.pen_up()
    
    def pen_down(self) -> None:
        """Lower pen."""
        if not self.connected:
            raise RuntimeError("Not connected to plotter")
        self.plotter.pen_down()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test plotter connection."""
        try:
            if self.connect():
                # Test basic movement
                self.pen_up()
                self.move_to(0, 0)
                self.pen_down()
                self.pen_up()
                
                self.disconnect()
                return {"success": True, "message": "Connection test passed"}
            else:
                return {"success": False, "message": "Failed to connect"}
        except Exception as e:
            return {"success": False, "message": str(e)}
```

---

## 6. Testing Guidelines

### Test Structure

Organize tests into logical groups:

```python
class Test[DriverName]Availability:
    """Test driver availability and installation."""
    
    def test_driver_available(self):
        """Test when driver is properly installed."""
        pass
    
    def test_driver_unavailable(self):
        """Test when driver dependencies are missing."""
        pass

class Test[DriverName]Manager:
    """Test manager functionality."""
    
    def test_initialization(self):
        """Test manager creation with various options."""
        pass
    
    def test_connection_workflow(self):
        """Test connect/disconnect cycle."""
        pass
    
    def test_device_operations(self):
        """Test basic device operations."""
        pass

class Test[DriverName]Detection:
    """Test hardware detection."""
    
    def test_device_detection(self):
        """Test device discovery."""
        pass
    
    def test_no_devices(self):
        """Test behavior when no devices found."""
        pass
```

### Mocking External Dependencies

Use mocks for hardware dependencies:

```python
from unittest.mock import Mock, patch

@patch('vfab.drivers.[driver_name].hardware_library')
def test_with_mock_hardware(mock_hardware):
    """Test driver behavior with mocked hardware."""
    mock_hardware.Plotter.return_value.connect.return_value = True
    
    manager = create_[driver_name]_manager()
    result = manager.connect()
    
    assert result is True
    mock_hardware.Plotter.return_value.connect.assert_called_once()
```

### Integration Testing

Test CLI integration:

```python
def test_driver_install_command():
    """Test driver installation via CLI."""
    from vfab.cli.driver.install import install_command
    from typer.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(install_command, ["[driver_name]"])
    
    assert result.exit_code == 0
    assert "installed successfully" in result.stdout
```

---

## 7. Configuration Integration

### Driver Configuration Schema

Add driver-specific configuration to the main config:

```python
# In src/vfab/config.py
class [DriverName]Config(BaseModel):
    """Configuration for [driver name] driver."""
    
    port: Optional[str] = None
    timeout: int = 5
    speed: int = 1000
    pen_height: int = 50
    auto_connect: bool = False

class DeviceConfig(BaseModel):
    """Main device configuration."""
    
    # Existing fields...
    axidraw_port: Optional[str] = None
    [driver_name]: [DriverName]Config = [DriverName]Config()
```

### Configuration File Example

```yaml
# config/config.yaml
device:
  # Existing device config...
  axidraw_port: null
  
  # New driver configuration
  simple_plotter:
    port: "/dev/ttyUSB0"
    timeout: 10
    speed: 1500
    pen_height: 60
    auto_connect: true
```

### Accessing Configuration in Driver

```python
class [DriverName]Manager:
    def __init__(self, port: Optional[str] = None, **options):
        # Load configuration
        try:
            from ..config import get_config
            config = get_config()
            driver_config = config.device.[driver_name]
            
            # Use config values if not overridden
            self.port = port or driver_config.port
            self.timeout = options.get('timeout', driver_config.timeout)
            self.speed = options.get('speed', driver_config.speed)
        except Exception:
            # Fallback to defaults
            self.port = port
            self.timeout = 5
            self.speed = 1000
```

---

## 8. Common Patterns

### Error Handling Patterns

```python
# Standard error handling for driver operations
def safe_device_operation(operation):
    """Wrapper for safe device operations."""
    try:
        return {"success": True, "result": operation()}
    except ImportError as e:
        return {"success": False, "error": f"Driver not available: {e}"}
    except ConnectionError as e:
        return {"success": False, "error": f"Connection failed: {e}"}
    except TimeoutError as e:
        return {"success": False, "error": f"Operation timed out: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}
```

### Connection Management

```python
class ConnectionManager:
    """Context manager for device connections."""
    
    def __init__(self, manager):
        self.manager = manager
    
    def __enter__(self):
        if not self.manager.connect():
            raise RuntimeError("Failed to connect to device")
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.manager.disconnect()

# Usage
with ConnectionManager(device_manager) as device:
    device.move_to(10, 10)
    device.pen_down()
```

### Device Detection Patterns

```python
# USB device detection
def detect_usb_devices(vendor_id: str, product_id_prefix: str) -> int:
    """Detect USB devices by vendor and product ID."""
    try:
        result = subprocess.run(
            ["lsusb"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            pattern = f"{vendor_id}:{product_id_prefix}"
            return sum(1 for line in result.stdout.split("\n") if pattern in line)
        return 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return 0

# Network device detection
def detect_network_devices(hosts: List[str], port: int) -> List[str]:
    """Detect network devices on specified hosts and port."""
    import socket
    
    available_devices = []
    for host in hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            if result == 0:
                available_devices.append(host)
            sock.close()
        except Exception:
            continue
    return available_devices
```

---

## 9. Troubleshooting

### Common Issues and Solutions

#### Import Errors

**Problem**: `ImportError: No module named 'hardware_library'`
**Solution**: 
- Check if dependencies are installed: `vfab driver list`
- Install missing dependencies: `vfab driver install [driver_name]`
- Verify package name in pyproject.toml

#### Connection Failures

**Problem**: Device connection fails consistently
**Solution**:
- Check device permissions: `ls -l /dev/tty*`
- Add user to appropriate groups: `sudo usermod -a -G dialout $USER`
- Verify device is not in use by other applications

#### Detection Issues

**Problem**: Hardware not detected
**Solution**:
- Check USB connections: `lsusb | grep vendor_id`
- Test with manufacturer tools
- Verify device compatibility

#### Configuration Problems

**Problem**: Driver configuration not loading
**Solution**:
- Validate config file: `vfab check config`
- Check YAML syntax: `python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"`
- Verify configuration schema

### Debugging Techniques

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In driver code
logger = logging.getLogger(__name__)
logger.debug(f"Connecting to device at {self.port}")
```

#### Test with Mock Hardware

```python
# For development without physical hardware
class Mock[DriverName]Manager:
    """Mock implementation for testing."""
    
    def __init__(self, port=None, **options):
        self.port = port
        self.connected = False
    
    def connect(self):
        # Simulate connection
        self.connected = True
        return True
    
    def move_to(self, x, y):
        if not self.connected:
            raise RuntimeError("Not connected")
        print(f"Mock move to ({x}, {y})")
```

#### CLI Debugging

```bash
# Test driver commands with verbose output
vfab driver info [driver_name] --verbose

# Test installation with debug output
vfab driver install [driver_name] --debug

# Check system status
vfab check system
```

### Getting Help

- **Documentation**: Check this guide and architecture docs
- **Examples**: Review existing AxiDraw driver implementation
- **Community**: Ask questions in project discussions
- **Issues**: Report bugs with detailed error information

---

## Conclusion

This guide provides a comprehensive framework for adding new drivers to vfab. By following these patterns and guidelines, you can create robust, well-integrated drivers that work seamlessly with the existing vfab ecosystem.

Remember to:
1. **Follow existing patterns** from the AxiDraw driver
2. **Write comprehensive tests** for all functionality
3. **Document your driver** with clear examples
4. **Handle errors gracefully** with informative messages
5. **Test thoroughly** with real and mock hardware

Happy coding! 🚀