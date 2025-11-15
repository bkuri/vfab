# Configuration Reference Cheat Sheet

## 🧭 Quick Navigation
- **Command line options?** [Command Line Reference](command-line.md)
- **Ready-made presets?** [Optimization Presets](optimization-presets.md)
- **Material settings?** [Materials Reference](materials-reference.md)
- **Performance tuning?** [Performance Tuning](../power-user/performance-tuning.md)

---

## **Configuration File Locations**

### **Default Locations**
```bash
# System-wide configuration
/etc/vfab/config.yaml

# User configuration  
~/.config/vfab/config.yaml

# Project configuration
./config/config.yaml

# Environment-specific
$PLOTTY_CONFIG_DIR/config.yaml
```

### **Configuration Priority**
1. Command line flags (highest)
2. Environment variables
3. Project config file
4. User config file
5. System config file (lowest)

## **Complete Configuration Schema**

### **Core vfab Configuration**
```yaml
# vfab main configuration
version: "1.0"

# Plotting settings
plotting:
  # Hardware settings
  hardware:
    device: "axidraw"           # axidraw, plotter, custom
    port: "/dev/ttyUSB0"        # Device port
    baud_rate: 115200           # Serial baud rate
    
  # Motion settings
  motion:
    speed: 40                   # Percentage (1-100)
    acceleration: 1.5           # Acceleration factor
    pen_up_height: 50           # Pen lift height (0-100)
    pen_down_force: 40          # Pen pressure (0-100)
    
  # Quality settings
  quality:
    precision: "medium"         # low, medium, high, ultra
    smoothing: true             # Enable path smoothing
    corner_handling: "smooth"   # sharp, smooth, rounded
    
  # Multi-pen settings
  multipen:
    enabled: false              # Enable multi-pen support
    pen_mapping: {}             # Pen mapping configuration
    auto_switch: true           # Automatic pen switching

# System settings
system:
  # Resource management
  resources:
    max_memory: "2GB"           # Maximum memory usage
    cpu_cores: 4                # Number of CPU cores to use
    temp_dir: "/tmp/vfab"     # Temporary directory
    
  # Performance settings
  performance:
    buffer_size: "64MB"         # I/O buffer size
    cache_enabled: true         # Enable caching
    parallel_processing: true   # Enable parallel processing
    
  # Logging
  logging:
    level: "INFO"               # DEBUG, INFO, WARNING, ERROR
    file: "/var/log/vfab/vfab.log"
    max_size: "100MB"           # Max log file size
    backup_count: 5             # Number of log backups

# Database settings
database:
  # Connection settings
  connection:
    type: "sqlite"              # sqlite, postgresql, mysql
    host: "localhost"
    port: 5432
    database: "vfab"
    username: "vfab_user"
    password: "secure_password"
    
  # Performance settings
  performance:
    connection_pool: 10         # Connection pool size
    query_timeout: 30           # Query timeout (seconds)
    batch_size: 50              # Batch operation size
    
  # Backup settings
  backup:
    enabled: true               # Enable automatic backups
    interval: "daily"           # daily, weekly, monthly
    retention: 30              # Backup retention (days)
    location: "/var/backups/vfab"

# Network settings
network:
  # Server settings
  server:
    enabled: true              # Enable network server
    host: "0.0.0.0"           # Server host
    port: 8080                # Server port
    ssl_enabled: false        # Enable SSL
    
  # Security
  security:
    api_key_required: false   # Require API key
    allowed_hosts: []          # Allowed host IPs
    rate_limiting: true       # Enable rate limiting
    
  # Performance
  performance:
    max_connections: 100      # Maximum concurrent connections
    timeout: 30               # Connection timeout
    compression: true         # Enable compression

# Guards and safety
guards:
  # Hardware guards
  hardware:
    enabled: true             # Enable hardware guards
    emergency_stop: true      # Emergency stop functionality
    boundary_check: true      # Plotting boundary checking
    
  # Job guards
  job:
    max_duration: "2h"        # Maximum job duration
    max_complexity: 10000     # Maximum path complexity
    size_limits:               # Size limits
      max_width: "1000mm"
      max_height: "1000mm"
      
  # System guards
  system:
    memory_limit: "4GB"       # System memory limit
    disk_space: "1GB"         # Minimum disk space required
    temperature_limit: 80      # Maximum temperature (°C)

# Hooks and automation
hooks:
  # Job hooks
  job:
    pre_start: []             # Scripts to run before job starts
    post_complete: []          # Scripts to run after job completes
    on_error: []              # Scripts to run on error
    
  # System hooks
  system:
    startup: []               # Scripts to run on system startup
    shutdown: []              # Scripts to run on system shutdown
    
  # Custom hooks
  custom: {}                  # Custom hook definitions

# Presets and profiles
presets:
  # Plotting presets
  plotting:
    draft:
      speed: 80
      precision: "low"
      force: 30
    quality:
      speed: 25
      precision: "high"
      force: 50
    balanced:
      speed: 50
      precision: "medium"
      force: 40
      
  # Material presets
  materials:
    paper_standard:
      pen_force: 40
      pen_speed: 40
    paper_thick:
      pen_force: 60
      pen_speed: 30
    film:
      pen_force: 25
      pen_speed: 50

# Integration settings
integrations:
  # vpype integration
  vpype:
    enabled: true
    presets_file: "config/vpype-presets.yaml"
    
  # External tools
  external_tools:
    inkscape_path: "/usr/bin/inkscape"
    illustrator_path: "/Applications/Adobe Illustrator.app"
    
  # Cloud services
  cloud:
    dropbox_enabled: false
    google_drive_enabled: false
    webhook_enabled: false
```

## **Environment Variables**

### **vfab Environment Variables**
```bash
# Configuration
export PLOTTY_CONFIG_DIR="/path/to/config"
export PLOTTY_DATA_DIR="/path/to/data"
export PLOTTY_LOG_LEVEL="INFO"

# Database
export PLOTTY_DB_URL="postgresql://user:pass@localhost/vfab"
export PLOTTY_DB_HOST="localhost"
export PLOTTY_DB_PORT="5432"
export PLOTTY_DB_NAME="vfab"
export PLOTTY_DB_USER="vfab_user"
export PLOTTY_DB_PASSWORD="secure_password"

# Hardware
export PLOTTY_DEVICE_PORT="/dev/ttyUSB0"
export PLOTTY_DEVICE_TYPE="axidraw"
export PLOTTY_PEN_UP_HEIGHT="50"
export PLOTTY_PEN_DOWN_FORCE="40"

# Network
export PLOTTY_SERVER_HOST="0.0.0.0"
export PLOTTY_SERVER_PORT="8080"
export PLOTTY_API_KEY="your_api_key_here"

# Performance
export PLOTTY_MAX_MEMORY="2GB"
export PLOTTY_CPU_CORES="4"
export PLOTTY_CACHE_ENABLED="true"

# Security
export PLOTTY_SSL_CERT_PATH="/path/to/cert.pem"
export PLOTTY_SSL_KEY_PATH="/path/to/key.pem"
```

## **Command Line Configuration**

### **Configuration Commands**
```bash
# View current configuration
vfab config show
vfab config show --section plotting
vfab config show --key plotting.speed

# Set configuration values
vfab config set plotting.speed 50
vfab config set logging.level DEBUG
vfab config set database.type postgresql

# Reset configuration
vfab config reset                    # Reset all
vfab config reset --section plotting  # Reset section
vfab config reset --key plotting.speed # Reset specific key

# Validate configuration
vfab config validate
vfab config validate --strict

# Export/Import configuration
vfab config export > my_config.yaml
vfab config import my_config.yaml

# Generate default configuration
vfab config generate --output default_config.yaml
vfab config generate --template minimal > minimal.yaml
```

### **Runtime Configuration Override**
```bash
# Override configuration for single command
vfab --config custom.yaml add design.svg
vfab --config-key plotting.speed=60 add design.svg
vfab --log-level DEBUG list

# Multiple overrides
vfab \
  --config-key plotting.speed=70 \
  --config-key plotting.precision=high \
  --config-key logging.level=DEBUG \
  add complex_design.svg
```

## **Configuration Templates**

### **Minimal Configuration**
```yaml
# minimal.yaml - Basic setup for quick start
version: "1.0"

plotting:
  hardware:
    device: "axidraw"
  motion:
    speed: 40
    pen_down_force: 40

system:
  logging:
    level: "INFO"

database:
  connection:
    type: "sqlite"
```

### **Development Configuration**
```yaml
# development.yaml - Optimized for development
version: "1.0"

plotting:
  hardware:
    device: "axidraw"
  motion:
    speed: 20  # Slower for testing
    pen_down_force: 30
  quality:
    precision: "high"

system:
  logging:
    level: "DEBUG"  # Verbose logging
    file: "dev_vfab.log"
  resources:
    temp_dir: "/tmp/vfab_dev"

database:
  connection:
    type: "sqlite"
    database: "dev_vfab.db"

guards:
  job:
    max_duration: "30m"  # Shorter for testing
```

### **Production Configuration**
```yaml
# production.yaml - Optimized for production use
version: "1.0"

plotting:
  hardware:
    device: "axidraw"
    port: "/dev/ttyUSB0"
  motion:
    speed: 50
    acceleration: 1.5
    pen_up_height: 60
    pen_down_force: 45
  quality:
    precision: "medium"
    smoothing: true

system:
  resources:
    max_memory: "4GB"
    cpu_cores: 8
  performance:
    buffer_size: "128MB"
    cache_enabled: true
    parallel_processing: true
  logging:
    level: "INFO"
    file: "/var/log/vfab/vfab.log"
    max_size: "100MB"
    backup_count: 10

database:
  connection:
    type: "postgresql"
    host: "localhost"
    port: 5432
    database: "vfab_prod"
    username: "vfab_user"
    password: "secure_password"
  performance:
    connection_pool: 20
    query_timeout: 60
  backup:
    enabled: true
    interval: "daily"
    retention: 90

network:
  server:
    enabled: true
    host: "0.0.0.0"
    port: 8080
    ssl_enabled: true
  security:
    api_key_required: true
    rate_limiting: true

guards:
  hardware:
    enabled: true
    emergency_stop: true
    boundary_check: true
  job:
    max_duration: "4h"
    max_complexity: 50000
  system:
    memory_limit: "8GB"
    disk_space: "5GB"

hooks:
  job:
    post_complete: ["scripts/notify_complete.sh"]
    on_error: ["scripts/notify_error.sh"]
```

### **High Performance Configuration**
```yaml
# high_performance.yaml - Maximum speed setup
version: "1.0"

plotting:
  hardware:
    device: "axidraw"
  motion:
    speed: 80              # High speed
    acceleration: 2.0       # High acceleration
    pen_up_height: 70       # Fast pen movement
    pen_down_force: 35      # Lighter force for speed
  quality:
    precision: "low"        # Lower precision for speed
    smoothing: false        # Disable smoothing for speed

system:
  resources:
    max_memory: "8GB"
    cpu_cores: "all"        # Use all available cores
  performance:
    buffer_size: "256MB"
    cache_enabled: true
    parallel_processing: true

database:
  connection:
    type: "postgresql"
  performance:
    connection_pool: 50
    query_timeout: 30
    batch_size: 100

network:
  performance:
    max_connections: 200
    compression: true
```

## **Configuration Validation**

### **Validation Rules**
```yaml
# validation_rules.yaml - Custom validation rules
rules:
  plotting:
    speed:
      type: "integer"
      min: 1
      max: 100
    pen_down_force:
      type: "integer"
      min: 0
      max: 100
    precision:
      type: "string"
      enum: ["low", "medium", "high", "ultra"]
      
  database:
    connection:
      type:
        enum: ["sqlite", "postgresql", "mysql"]
      port:
        type: "integer"
        min: 1
        max: 65535
        
  system:
    resources:
      max_memory:
        type: "string"
        pattern: "^[0-9]+[KMGT]?B$"
```

### **Custom Validation Script**
```python
# validate_config.py
import yaml
import jsonschema
from pathlib import Path

class ConfigValidator:
    def __init__(self, schema_file="config_schema.json"):
        with open(schema_file) as f:
            self.schema = json.load(f)
    
    def validate_config(self, config_file):
        """Validate configuration file against schema"""
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        try:
            jsonschema.validate(config, self.schema)
            print(f"✓ {config_file} is valid")
            return True
        except jsonschema.ValidationError as e:
            print(f"✗ {config_file} validation failed:")
            print(f"  {e.message}")
            if e.path:
                print(f"  Path: {' -> '.join(map(str, e.path))}")
            return False
        except Exception as e:
            print(f"✗ Error validating {config_file}: {e}")
            return False
    
    def validate_all_configs(self, config_dir="config"):
        """Validate all YAML files in directory"""
        config_path = Path(config_dir)
        valid_count = 0
        total_count = 0
        
        for yaml_file in config_path.glob("*.yaml"):
            total_count += 1
            if self.validate_config(yaml_file):
                valid_count += 1
        
        print(f"\nValidation complete: {valid_count}/{total_count} files valid")
        return valid_count == total_count

# Usage
if __name__ == "__main__":
    validator = ConfigValidator()
    validator.validate_all_configs()
```

## **Configuration Management**

### **Configuration Profiles**
```bash
#!/bin/bash
# config_profiles.sh - Manage multiple configuration profiles

CONFIG_DIR="$HOME/.config/vfab/profiles"

create_profile() {
    local profile_name=$1
    local profile_dir="$CONFIG_DIR/$profile_name"
    
    mkdir -p "$profile_dir"
    
    # Generate default config for profile
    vfab config generate --template minimal > "$profile_dir/config.yaml"
    
    echo "Created profile: $profile_name"
    echo "Edit: $profile_dir/config.yaml"
}

switch_profile() {
    local profile_name=$1
    local profile_dir="$CONFIG_DIR/$profile_name"
    local current_config="$HOME/.config/vfab/config.yaml"
    
    if [ ! -d "$profile_dir" ]; then
        echo "Profile '$profile_name' does not exist"
        return 1
    fi
    
    # Backup current config
    if [ -f "$current_config" ]; then
        cp "$current_config" "$current_config.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Switch to new profile
    ln -sf "$profile_dir/config.yaml" "$current_config"
    
    echo "Switched to profile: $profile_name"
}

list_profiles() {
    echo "Available profiles:"
    for profile in "$CONFIG_DIR"/*; do
        if [ -d "$profile" ]; then
            profile_name=$(basename "$profile")
            if [ -L "$HOME/.config/vfab/config.yaml" ]; then
                current_target=$(readlink "$HOME/.config/vfab/config.yaml")
                if [ "$current_target" = "$profile/config.yaml" ]; then
                    echo "  * $profile_name (active)"
                else
                    echo "    $profile_name"
                fi
            else
                echo "    $profile_name"
            fi
        fi
    done
}

# Usage examples:
# create_profile "production"
# switch_profile "production"
# list_profiles
```

## **Related Cheat Sheets**
- [Command Line Reference](command-line.md) - All command line options
- [Optimization Presets](optimization-presets.md) - Pre-built optimization settings
- [Materials Reference](materials-reference.md) - Material-specific configurations

## **Configuration Tips**
- **Use version control**: Keep your configuration files in git
- **Environment separation**: Use different configs for dev/staging/production
- **Security**: Never commit passwords or API keys to version control
- **Validation**: Always validate configuration changes before deployment
- **Documentation**: Document custom configuration values and their purposes