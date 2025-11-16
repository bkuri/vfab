# Driver Architecture

This document describes the architecture and design patterns of the vfab driver system. Understanding this architecture is essential for developing new drivers and maintaining the existing system.

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Component Interfaces](#2-component-interfaces)
3. [Detection Patterns](#3-detection-patterns)
4. [Configuration Integration](#4-configuration-integration)
5. [Error Handling](#5-error-handling)
6. [Lifecycle Management](#6-lifecycle-management)
7. [Extension Points](#7-extension-points)
8. [Communication Patterns](#8-communication-patterns)
9. [Performance Considerations](#9-performance-considerations)

---

## 1. System Overview

The vfab driver system follows a layered architecture with clear separation of concerns. Each layer has specific responsibilities and well-defined interfaces.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Install   │ │    Info     │ │    Test     │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  Management Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Driver    │ │  Detection  │ │  Config     │ │
│  │   Manager   │ │   System    │ │  System     │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  Hardware Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Plotter   │ │   Camera    │ │   Sensor    │ │
│  │   Drivers   │ │   Drivers   │ │   Drivers   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Command → CLI Interface → Driver Manager → Hardware Interface → Physical Device
     ↓              ↓              ↓               ↓                ↓
Validation → Processing → State Management → Protocol Handling → Device Response
     ↓              ↓              ↓               ↓                ↓
   Error ← CLI Output ← Status Update ← Event Handling ← Hardware Events
```

### Key Design Principles

1. **Modularity**: Each driver is self-contained with minimal dependencies
2. **Extensibility**: New drivers can be added without modifying existing code
3. **Consistency**: All drivers follow the same interface patterns
4. **Reliability**: Robust error handling and recovery mechanisms
5. **Performance**: Efficient resource usage and minimal overhead

---

## 2. Component Interfaces

### Driver Interface Contract

All hardware drivers must implement these core interfaces:

#### Availability Interface

```python
def is_[driver_name]_available() -> bool:
    """Check if driver dependencies are available.
    
    This function should:
    - Import required dependencies safely
    - Return True if all dependencies are available
    - Return False if any dependency is missing
    - Not raise exceptions for missing dependencies
    
    Returns:
        bool: True if driver can be used, False otherwise
    """

def get_[driver_name]_install_instructions() -> str:
    """Get installation instructions for missing dependencies.
    
    Returns:
        str: Human-readable installation instructions
    """
```

#### Factory Interface

```python
def create_[driver_name]_manager(**kwargs) -> [DriverName]Manager:
    """Factory function to create driver manager.
    
    This function should:
    - Validate driver availability
    - Create manager instance with configuration
    - Apply default settings from config
    - Raise ImportError if driver is not available
    
    Args:
        **kwargs: Driver-specific configuration options
        
    Returns:
        [DriverName]Manager: Configured manager instance
        
    Raises:
        ImportError: If driver dependencies are not available
    """
```

#### Manager Interface

```python
class [DriverName]Manager:
    """Main driver manager interface."""
    
    def __init__(self, **options):
        """Initialize manager with configuration options."""
        
    def connect(self) -> bool:
        """Establish connection to hardware device.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        
    def disconnect(self) -> None:
        """Close connection to hardware device."""
        
    def is_connected(self) -> bool:
        """Check if device is currently connected.
        
        Returns:
            bool: Connection status
        """
        
    def test_connection(self) -> Dict[str, Any]:
        """Test device functionality and return results.
        
        Returns:
            Dict with test results:
            - success: bool - Overall test success
            - message: str - Human-readable result
            - details: dict - Additional test information
        """
```

### Detection Interface

```python
class DeviceDetector:
    """Hardware detection system."""
    
    def detect_[driver_name]_devices(self) -> Dict[str, Any]:
        """Detect devices for specific driver.
        
        Returns:
            Dict with detection results:
            - count: int - Number of devices found
            - installed: bool - Whether driver is installed
            - device_id: str - Hardware identifier
            - device_name: str - Human-readable name
            - accessible: bool - Whether devices are accessible
            - devices: List[Dict] - Detailed device information
        """
```

### Configuration Interface

```python
class [DriverName]Config(BaseModel):
    """Driver-specific configuration model.
    
    All driver configs should:
    - Inherit from Pydantic BaseModel
    - Provide sensible defaults
    - Include comprehensive validation
    - Support environment variable overrides
    """
```

---

## 3. Detection Patterns

### Hardware Detection Strategies

#### USB Device Detection

```python
def detect_usb_devices(vendor_id: str, product_prefix: str) -> Dict[str, Any]:
    """Detect USB devices by vendor and product ID.
    
    This pattern:
    - Uses lsusb for device enumeration
    - Filters by vendor ID and product prefix
    - Provides device details and accessibility
    - Handles permission errors gracefully
    """
    result = {
        "count": 0,
        "devices": [],
        "accessible": False
    }
    
    try:
        # Enumerate USB devices
        lsusb_output = subprocess.run(
            ["lsusb"], capture_output=True, text=True, timeout=5
        )
        
        if lsusb_output.returncode == 0:
            # Parse and filter devices
            for line in lsusb_output.stdout.split('\n'):
                if vendor_id in line and product_prefix in line:
                    device_info = parse_lsusb_line(line)
                    result["devices"].append(device_info)
                    result["count"] += 1
            
            # Test accessibility if devices found
            if result["count"] > 0:
                result["accessible"] = test_usb_access(result["devices"])
                
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # lsusb not available or timed out
        pass
    except Exception as e:
        # Log error but don't fail detection
        logger.warning(f"USB detection failed: {e}")
    
    return result
```

#### Network Device Detection

```python
def detect_network_devices(hosts: List[str], port: int, timeout: int = 1) -> Dict[str, Any]:
    """Detect network devices using TCP connection testing.
    
    This pattern:
    - Tests connectivity to multiple hosts
    - Uses non-blocking sockets with timeout
    - Returns responsive hosts and services
    - Handles network errors gracefully
    """
    result = {
        "count": 0,
        "devices": [],
        "accessible": False
    }
    
    for host in hosts:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                connection_result = sock.connect_ex((host, port))
                
                if connection_result == 0:
                    device_info = {
                        "host": host,
                        "port": port,
                        "responsive": True,
                        "response_time": measure_response_time(host, port)
                    }
                    result["devices"].append(device_info)
                    result["count"] += 1
                    
        except Exception as e:
            logger.debug(f"Network detection failed for {host}: {e}")
    
    result["accessible"] = result["count"] > 0
    return result
```

#### Serial Device Detection

```python
def detect_serial_devices(baud_rates: List[int] = None) -> Dict[str, Any]:
    """Detect serial devices by testing communication.
    
    This pattern:
    - Scans available serial ports
    - Tests communication at different baud rates
    - Identifies device types by response patterns
    - Handles permission and access issues
    """
    result = {
        "count": 0,
        "devices": [],
        "accessible": False
    }
    
    if baud_rates is None:
        baud_rates = [9600, 115200, 38400]
    
    try:
        import serial.tools.list_ports
        
        # Get all available serial ports
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            device_info = {
                "port": port.device,
                "description": port.description,
                "manufacturer": port.manufacturer,
                "product": port.product
            }
            
            # Test communication at different baud rates
            for baud in baud_rates:
                try:
                    with serial.Serial(port.device, baud, timeout=1) as ser:
                        # Send identification command
                        ser.write(b'ID\r\n')
                        response = ser.read(100)
                        
                        if response:
                            device_info["baud_rate"] = baud
                            device_info["identification"] = response.decode('utf-8', errors='ignore')
                            break
                            
                except Exception:
                    continue
            
            result["devices"].append(device_info)
            result["count"] += 1
            
    except ImportError:
        logger.warning("pyserial not available for serial device detection")
    except Exception as e:
        logger.warning(f"Serial detection failed: {e}")
    
    result["accessible"] = result["count"] > 0
    return result
```

### Detection Best Practices

1. **Timeout Handling**: Always use timeouts for hardware operations
2. **Permission Checking**: Test device accessibility, not just presence
3. **Error Resilience**: Don't fail detection for individual device errors
4. **Logging**: Log detection attempts and failures for debugging
5. **Caching**: Cache detection results for performance (with TTL)

---

## 4. Configuration Integration

### Configuration Hierarchy

```
Priority (high to low):
1. Command Line Arguments
2. Environment Variables
3. Configuration File (config.yaml)
4. Default Values
```

### Configuration Loading Pattern

```python
class ConfigurationManager:
    """Manages driver configuration with multiple sources."""
    
    def __init__(self, driver_name: str):
        self.driver_name = driver_name
        self._config_cache = None
    
    def get_config(self) -> [DriverName]Config:
        """Get merged configuration from all sources."""
        if self._config_cache is None:
            self._config_cache = self._load_config()
        return self._config_cache
    
    def _load_config(self) -> [DriverName]Config:
        """Load configuration from all sources."""
        # Start with defaults
        config_dict = [DriverName]Config().model_dump()
        
        # Override with config file
        file_config = self._load_file_config()
        if file_config:
            config_dict.update(file_config)
        
        # Override with environment variables
        env_config = self._load_env_config()
        if env_config:
            config_dict.update(env_config)
        
        # Validate and create config object
        return [DriverName]Config(**config_dict)
    
    def _load_file_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            from ..config import get_config
            main_config = get_config()
            
            if hasattr(main_config.device, self.driver_name):
                return main_config.device[self.driver_name].model_dump()
        except Exception as e:
            logger.warning(f"Failed to load file config: {e}")
        
        return {}
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_prefix = f"VFAB_{self.driver_name.upper()}_"
        env_config = {}
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                env_config[config_key] = self._parse_env_value(value)
        
        return env_config
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        # Handle boolean values
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Handle numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
```

### Configuration Schema Pattern

```python
class [DriverName]Config(BaseModel):
    """Configuration for [driver name] driver."""
    
    # Connection settings
    port: Optional[str] = Field(
        None,
        description="Device port or connection identifier"
    )
    timeout: int = Field(
        5,
        ge=1, le=60,
        description="Connection timeout in seconds"
    )
    
    # Device settings
    speed: int = Field(
        1000,
        ge=1, le=10000,
        description="Device operation speed"
    )
    
    # Advanced options
    auto_connect: bool = Field(
        False,
        description="Automatically connect on initialization"
    )
    
    retry_count: int = Field(
        3,
        ge=0, le=10,
        description="Number of connection retry attempts"
    )
    
    class Config:
        env_prefix = "vfab_[driver_name]"
        case_sensitive = False
```

---

## 5. Error Handling

### Error Classification

```python
from enum import Enum
from typing import Optional

class DriverErrorType(Enum):
    """Classification of driver errors."""
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"
    PERMISSION_ERROR = "permission_error"
    CONFIGURATION_ERROR = "configuration_error"
    HARDWARE_ERROR = "hardware_error"
    PROTOCOL_ERROR = "protocol_error"
    DEPENDENCY_ERROR = "dependency_error"

class DriverError(Exception):
    """Structured driver error with context."""
    
    def __init__(
        self,
        message: str,
        error_type: DriverErrorType,
        driver_name: str,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.driver_name = driver_name
        self.context = context or {}
        self.original_error = original_error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            "error": self.message,
            "type": self.error_type.value,
            "driver": self.driver_name,
            "context": self.context,
            "original_error": str(self.original_error) if self.original_error else None
        }
```

### Error Handling Patterns

```python
class ErrorHandler:
    """Centralized error handling for driver operations."""
    
    def __init__(self, driver_name: str):
        self.driver_name = driver_name
        self.logger = logging.getLogger(f"vfab.drivers.{driver_name}")
    
    def handle_operation(self, operation: callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute operation with comprehensive error handling."""
        try:
            result = operation(*args, **kwargs)
            return {"success": True, "result": result}
            
        except ImportError as e:
            error = DriverError(
                message=f"Driver dependencies not available: {e}",
                error_type=DriverErrorType.DEPENDENCY_ERROR,
                driver_name=self.driver_name,
                original_error=e
            )
            self.logger.error(error.to_dict())
            return {"success": False, "error": error}
            
        except PermissionError as e:
            error = DriverError(
                message=f"Permission denied accessing device: {e}",
                error_type=DriverErrorType.PERMISSION_ERROR,
                driver_name=self.driver_name,
                context={"suggestion": "Check device permissions and user groups"},
                original_error=e
            )
            self.logger.error(error.to_dict())
            return {"success": False, "error": error}
            
        except TimeoutError as e:
            error = DriverError(
                message=f"Operation timed out: {e}",
                error_type=DriverErrorType.TIMEOUT_ERROR,
                driver_name=self.driver_name,
                context={"timeout": kwargs.get('timeout', 'default')},
                original_error=e
            )
            self.logger.warning(error.to_dict())
            return {"success": False, "error": error}
            
        except ConnectionError as e:
            error = DriverError(
                message=f"Connection failed: {e}",
                error_type=DriverErrorType.CONNECTION_ERROR,
                driver_name=self.driver_name,
                context={"port": kwargs.get('port')},
                original_error=e
            )
            self.logger.error(error.to_dict())
            return {"success": False, "error": error}
            
        except Exception as e:
            error = DriverError(
                message=f"Unexpected error: {e}",
                error_type=DriverErrorType.HARDWARE_ERROR,
                driver_name=self.driver_name,
                original_error=e
            )
            self.logger.exception(error.to_dict())
            return {"success": False, "error": error}
```

### Recovery Strategies

```python
class ConnectionRecovery:
    """Implements connection recovery strategies."""
    
    def __init__(self, manager, max_retries: int = 3):
        self.manager = manager
        self.max_retries = max_retries
        self.retry_count = 0
    
    def connect_with_recovery(self) -> bool:
        """Connect with automatic recovery."""
        while self.retry_count < self.max_retries:
            try:
                if self.manager.connect():
                    self.retry_count = 0  # Reset on success
                    return True
                    
            except Exception as e:
                self.retry_count += 1
                self.logger.warning(f"Connection attempt {self.retry_count} failed: {e}")
                
                # Implement recovery strategy
                if self.retry_count < self.max_retries:
                    self._apply_recovery_strategy()
                    time.sleep(2 ** self.retry_count)  # Exponential backoff
        
        return False
    
    def _apply_recovery_strategy(self):
        """Apply recovery strategy based on retry count."""
        if self.retry_count == 1:
            # First retry: reset connection
            self.manager.disconnect()
            
        elif self.retry_count == 2:
            # Second retry: reset device
            self.manager.reset_device()
            
        else:
            # Later retries: full reinitialization
            self.manager.reinitialize()
```

---

## 6. Lifecycle Management

### Driver Lifecycle States

```python
from enum import Enum

class DriverState(Enum):
    """Driver lifecycle states."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    BUSY = "busy"
    ERROR = "error"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"

class DriverLifecycle:
    """Manages driver lifecycle with state transitions."""
    
    def __init__(self, manager):
        self.manager = manager
        self.state = DriverState.UNINITIALIZED
        self.state_listeners = []
        self.logger = logging.getLogger(f"vfab.drivers.{manager.__class__.__name__}")
    
    def add_state_listener(self, listener: callable):
        """Add listener for state changes."""
        self.state_listeners.append(listener)
    
    def _set_state(self, new_state: DriverState):
        """Set new state and notify listeners."""
        old_state = self.state
        self.state = new_state
        
        self.logger.debug(f"State transition: {old_state.value} -> {new_state.value}")
        
        for listener in self.state_listeners:
            try:
                listener(old_state, new_state)
            except Exception as e:
                self.logger.error(f"State listener error: {e}")
    
    def initialize(self) -> bool:
        """Initialize driver."""
        self._set_state(DriverState.INITIALIZING)
        
        try:
            # Perform initialization
            self.manager._initialize_hardware()
            self._set_state(DriverState.READY)
            return True
            
        except Exception as e:
            self._set_state(DriverState.ERROR)
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def connect(self) -> bool:
        """Connect to device."""
        if self.state != DriverState.READY:
            self.logger.warning(f"Cannot connect from state: {self.state.value}")
            return False
        
        self._set_state(DriverState.CONNECTING)
        
        try:
            if self.manager.connect():
                self._set_state(DriverState.CONNECTED)
                return True
            else:
                self._set_state(DriverState.READY)
                return False
                
        except Exception as e:
            self._set_state(DriverState.ERROR)
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def shutdown(self):
        """Shutdown driver gracefully."""
        self._set_state(DriverState.SHUTTING_DOWN)
        
        try:
            if self.state == DriverState.CONNECTED:
                self.manager.disconnect()
            
            self.manager._cleanup_resources()
            self._set_state(DriverState.SHUTDOWN)
            
        except Exception as e:
            self._set_state(DriverState.ERROR)
            self.logger.error(f"Shutdown failed: {e}")
```

### Resource Management

```python
class ResourceManager:
    """Manages driver resources with automatic cleanup."""
    
    def __init__(self):
        self.resources = []
        self.cleanup_handlers = []
    
    def register_resource(self, resource: Any, cleanup_handler: callable = None):
        """Register a resource for automatic cleanup."""
        self.resources.append(resource)
        if cleanup_handler:
            self.cleanup_handlers.append(cleanup_handler)
    
    def cleanup_all(self):
        """Cleanup all registered resources."""
        for resource, handler in zip(self.resources, self.cleanup_handlers):
            try:
                handler(resource)
            except Exception as e:
                logger.warning(f"Resource cleanup failed: {e}")
        
        self.resources.clear()
        self.cleanup_handlers.clear()

# Usage with context manager
class DriverContext:
    """Context manager for driver operations."""
    
    def __init__(self, manager):
        self.manager = manager
        self.resource_manager = ResourceManager()
    
    def __enter__(self):
        self.resource_manager.register_resource(self.manager, lambda m: m.disconnect())
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.resource_manager.cleanup_all()
```

---

## 7. Extension Points

### Plugin System

```python
class DriverPlugin:
    """Base class for driver plugins."""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
    
    def get_driver_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.name,
            "version": self.version,
            "type": "driver_plugin"
        }
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with configuration."""
        raise NotImplementedError
    
    def get_manager_class(self) -> Type:
        """Get the manager class provided by this plugin."""
        raise NotImplementedError

class PluginManager:
    """Manages driver plugins."""
    
    def __init__(self):
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        """Load plugins from standard locations."""
        plugin_paths = [
            Path.home() / ".vfab" / "plugins",
            Path("/etc/vfab/plugins"),
            Path(__file__).parent / "plugins"
        ]
        
        for plugin_path in plugin_paths:
            if plugin_path.exists():
                self._load_plugins_from_path(plugin_path)
    
    def _load_plugins_from_path(self, path: Path):
        """Load plugins from a specific path."""
        for plugin_file in path.glob("*.py"):
            try:
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem, plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Register plugin
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, DriverPlugin) and 
                        attr != DriverPlugin):
                        
                        plugin = attr()
                        self.plugins[plugin.name] = plugin
                        
            except Exception as e:
                logger.warning(f"Failed to load plugin {plugin_file}: {e}")
    
    def get_plugin(self, name: str) -> Optional[DriverPlugin]:
        """Get plugin by name."""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all available plugins."""
        return [plugin.get_driver_info() for plugin in self.plugins.values()]
```

### Custom Detection Handlers

```python
class DetectionHandler:
    """Base class for custom detection handlers."""
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
    
    def detect(self) -> Dict[str, Any]:
        """Perform device detection."""
        raise NotImplementedError
    
    def is_compatible(self, device_info: Dict[str, Any]) -> bool:
        """Check if handler is compatible with device."""
        raise NotImplementedError

class DetectionRegistry:
    """Registry for detection handlers."""
    
    def __init__(self):
        self.handlers = []
    
    def register_handler(self, handler: DetectionHandler):
        """Register a detection handler."""
        self.handlers.append(handler)
        # Sort by priority (higher priority first)
        self.handlers.sort(key=lambda h: h.priority, reverse=True)
    
    def detect_all(self) -> Dict[str, Any]:
        """Run all detection handlers."""
        results = {}
        
        for handler in self.handlers:
            try:
                result = handler.detect()
                if result.get("count", 0) > 0:
                    results[handler.name] = result
            except Exception as e:
                logger.warning(f"Detection handler {handler.name} failed: {e}")
        
        return results
```

---

## 8. Communication Patterns

### Asynchronous Operations

```python
import asyncio
from typing import Awaitable, Callable

class AsyncDriverManager:
    """Asynchronous driver manager for non-blocking operations."""
    
    def __init__(self):
        self.loop = None
        self.operations = {}
    
    async def connect_async(self) -> bool:
        """Asynchronous connection."""
        try:
            # Run blocking connection in thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.connect
            )
            return result
        except Exception as e:
            logger.error(f"Async connection failed: {e}")
            return False
    
    async def execute_operation(
        self, 
        operation: Callable, 
        *args, 
        timeout: float = 5.0
    ) -> Dict[str, Any]:
        """Execute operation with timeout."""
        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, operation, *args),
                timeout=timeout
            )
            return {"success": True, "result": result}
        except asyncio.TimeoutError:
            return {"success": False, "error": "Operation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def monitor_device(self, callback: Callable) -> None:
        """Monitor device state changes."""
        while True:
            try:
                state = await self.get_state_async()
                await callback(state)
                await asyncio.sleep(1)  # Polling interval
            except Exception as e:
                logger.error(f"Device monitoring error: {e}")
                await asyncio.sleep(5)  # Backoff on error
```

### Event-Driven Communication

```python
from typing import Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DriverEvent:
    """Driver event data structure."""
    event_type: str
    timestamp: datetime
    driver_name: str
    data: Dict[str, Any]
    source: str = "driver"

class EventManager:
    """Manages driver events and listeners."""
    
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self.event_history: List[DriverEvent] = []
        self.max_history = 1000
    
    def subscribe(self, event_type: str, listener: Callable):
        """Subscribe to specific event type."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)
    
    def unsubscribe(self, event_type: str, listener: Callable):
        """Unsubscribe from event type."""
        if event_type in self.listeners:
            try:
                self.listeners[event_type].remove(listener)
            except ValueError:
                pass
    
    def emit(self, event: DriverEvent):
        """Emit event to all subscribers."""
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Notify listeners
        if event.event_type in self.listeners:
            for listener in self.listeners[event.event_type]:
                try:
                    listener(event)
                except Exception as e:
                    logger.error(f"Event listener error: {e}")
    
    def get_recent_events(
        self, 
        event_type: str = None, 
        since: datetime = None
    ) -> List[DriverEvent]:
        """Get recent events with optional filtering."""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        return events

# Usage in driver
class EventDrivenManager:
    """Manager with event-driven communication."""
    
    def __init__(self):
        self.event_manager = EventManager()
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event handlers for device state changes."""
        self.event_manager.subscribe("connection_changed", self._on_connection_changed)
        self.event_manager.subscribe("device_error", self._on_device_error)
        self.event_manager.subscribe("state_update", self._on_state_update)
    
    def _on_connection_changed(self, event: DriverEvent):
        """Handle connection state changes."""
        logger.info(f"Connection state changed: {event.data}")
    
    def _on_device_error(self, event: DriverEvent):
        """Handle device errors."""
        logger.error(f"Device error: {event.data}")
        # Implement error recovery
        self._handle_error_recovery(event.data)
    
    def _on_state_update(self, event: DriverEvent):
        """Handle device state updates."""
        # Update internal state
        self.current_state = event.data
```

---

## 9. Performance Considerations

### Connection Pooling

```python
class ConnectionPool:
    """Manages pool of device connections."""
    
    def __init__(self, manager_factory: Callable, max_connections: int = 5):
        self.manager_factory = manager_factory
        self.max_connections = max_connections
        self.available = []
        self.in_use = []
        self.total_created = 0
    
    def get_connection(self, **kwargs) -> Any:
        """Get connection from pool."""
        # Try to reuse existing connection
        for manager in self.available:
            if self._is_compatible(manager, kwargs):
                self.available.remove(manager)
                self.in_use.append(manager)
                return manager
        
        # Create new connection if under limit
        if self.total_created < self.max_connections:
            manager = self.manager_factory(**kwargs)
            self.in_use.append(manager)
            self.total_created += 1
            return manager
        
        # Pool exhausted
        raise RuntimeError("Connection pool exhausted")
    
    def release_connection(self, manager: Any):
        """Release connection back to pool."""
        if manager in self.in_use:
            self.in_use.remove(manager)
            
            # Test connection before returning to pool
            if self._test_connection(manager):
                self.available.append(manager)
            else:
                self._cleanup_connection(manager)
                self.total_created -= 1
    
    def _is_compatible(self, manager: Any, kwargs: Dict) -> bool:
        """Check if manager is compatible with requested parameters."""
        # Implement compatibility checking
        return True
    
    def _test_connection(self, manager: Any) -> bool:
        """Test if connection is still valid."""
        try:
            return manager.is_connected()
        except Exception:
            return False
    
    def _cleanup_connection(self, manager: Any):
        """Cleanup connection resources."""
        try:
            manager.disconnect()
        except Exception:
            pass
```

### Caching Strategies

```python
from functools import lru_cache
from typing import Optional, Any
import time

class DriverCache:
    """Caching system for driver operations."""
    
    def __init__(self, ttl: int = 300):  # 5 minutes default TTL
        self.ttl = ttl
        self.cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]  # Expired entry
        return None
    
    def set(self, key: str, value: Any):
        """Set cached value."""
        self.cache[key] = (value, time.time())
    
    def invalidate(self, key: str = None):
        """Invalidate cache entry or entire cache."""
        if key:
            self.cache.pop(key, None)
        else:
            self.cache.clear()

# Usage in driver
class CachedManager:
    """Manager with caching capabilities."""
    
    def __init__(self):
        self.cache = DriverCache(ttl=60)  # 1 minute cache
    
    @lru_cache(maxsize=128)
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information with caching."""
        # Check cache first
        cached_info = self.cache.get("device_info")
        if cached_info:
            return cached_info
        
        # Get fresh information
        info = self._query_device()
        
        # Cache the result
        self.cache.set("device_info", info)
        return info
    
    def invalidate_cache(self):
        """Invalidate all cached information."""
        self.cache.invalidate()
        self.get_device_info.cache_clear()
```

### Resource Monitoring

```python
import psutil
import threading
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ResourceUsage:
    """Resource usage statistics."""
    cpu_percent: float
    memory_mb: float
    open_files: int
    thread_count: int
    timestamp: float

class ResourceMonitor:
    """Monitor driver resource usage."""
    
    def __init__(self, driver_name: str):
        self.driver_name = driver_name
        self.monitoring = False
        self.usage_history: List[ResourceUsage] = []
        self.max_history = 1000
        self.monitor_thread = None
    
    def start_monitoring(self, interval: float = 1.0):
        """Start resource monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                usage = ResourceUsage(
                    cpu_percent=process.cpu_percent(),
                    memory_mb=process.memory_info().rss / 1024 / 1024,
                    open_files=len(process.open_files()),
                    thread_count=process.num_threads(),
                    timestamp=time.time()
                )
                
                self.usage_history.append(usage)
                if len(self.usage_history) > self.max_history:
                    self.usage_history.pop(0)
                
                # Check for resource warnings
                self._check_resource_warnings(usage)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.warning(f"Resource monitoring error: {e}")
                time.sleep(interval)
    
    def _check_resource_warnings(self, usage: ResourceUsage):
        """Check for resource usage warnings."""
        if usage.cpu_percent > 80:
            logger.warning(f"High CPU usage: {usage.cpu_percent}%")
        
        if usage.memory_mb > 500:  # 500MB threshold
            logger.warning(f"High memory usage: {usage.memory_mb}MB")
        
        if usage.open_files > 100:
            logger.warning(f"High file handle count: {usage.open_files}")
    
    def get_average_usage(self, duration: float = 60.0) -> ResourceUsage:
        """Get average resource usage over duration."""
        cutoff_time = time.time() - duration
        recent_usage = [
            u for u in self.usage_history 
            if u.timestamp >= cutoff_time
        ]
        
        if not recent_usage:
            return ResourceUsage(0, 0, 0, 0, time.time())
        
        return ResourceUsage(
            cpu_percent=sum(u.cpu_percent for u in recent_usage) / len(recent_usage),
            memory_mb=sum(u.memory_mb for u in recent_usage) / len(recent_usage),
            open_files=sum(u.open_files for u in recent_usage) / len(recent_usage),
            thread_count=sum(u.thread_count for u in recent_usage) / len(recent_usage),
            timestamp=time.time()
        )
```

---

## Conclusion

The vfab driver architecture provides a robust, extensible foundation for hardware integration. By following these patterns and interfaces, developers can create drivers that:

1. **Integrate seamlessly** with the existing system
2. **Handle errors gracefully** with comprehensive recovery
3. **Perform efficiently** with resource management
4. **Scale appropriately** with connection pooling and caching
5. **Communicate effectively** through events and async operations

The architecture is designed to evolve while maintaining backward compatibility and providing clear extension points for future enhancements.

For implementation details and step-by-step guidance, see the [Driver Development Guide](development.md).