# Daemon Command Reference

Complete reference for the vfab daemon process and WebSocket server.

## Overview

The vfab daemon (`vfab daemon`) is a long-running background process that manages:
- Job queue processing and execution
- WebSocket server for real-time monitoring
- Hardware device management
- System state coordination

## Command Syntax

```bash
vfab daemon [OPTIONS]
```

## Options

### `--host, -h`
**Default:** `localhost`  
**Description:** WebSocket server bind address

**Examples:**
```bash
# Bind to localhost (default)
vfab daemon

# Bind to all interfaces
vfab daemon --host 0.0.0.0

# Bind to specific network interface
vfab daemon --host 192.168.1.100
```

### `--port, -p`
**Default:** `8766`  
**Description:** WebSocket server port

**Examples:**
```bash
# Use default port
vfab daemon

# Use custom port
vfab daemon --port 8080

# Use port in production range
vfab daemon --port 8765
```

### `--workspace, -w`
**Default:** `$XDG_DATA_HOME/vfab/workspace`  
**Description:** Working directory for jobs and data

**Examples:**
```bash
# Use default workspace
vfab daemon

# Use custom workspace
vfab daemon --workspace /mnt/storage/vfab-workspace

# Use relative workspace
vfab daemon --workspace ./my-workspace
```

### `--log-level, -l`
**Default:** `info`  
**Description:** Logging verbosity level

**Available Levels:**
- `debug` - Detailed debugging information
- `info` - General operational information
- `warning` - Warning messages
- `error` - Error messages only
- `critical` - Critical errors only

**Examples:**
```bash
# Default info level
vfab daemon

# Debug mode for troubleshooting
vfab daemon --log-level debug

# Production mode (errors only)
vfab daemon --log-level error
```

### `--config, -c`
**Default:** `$XDG_CONFIG_HOME/vfab/config.yaml`  
**Description:** Path to configuration file

**Examples:**
```bash
# Use default config
vfab daemon

# Use custom config
vfab daemon --config /etc/vfab/production.yaml

# Use project-specific config
vfab daemon --config ./studio-config.yaml
```

### `--pid-file`
**Default:** None  
**Description:** Path to PID file for process management

**Examples:**
```bash
# Create PID file
vfab daemon --pid-file /var/run/vfab/vfab.pid

# Use user-local PID file
vfab daemon --pid-file ~/.local/run/vfab.pid
```

### `--daemonize, -d`
**Default:** `false`  
**Description:** Run as background daemon process

**Examples:**
```bash
# Run in foreground (default)
vfab daemon

# Run as background daemon
vfab daemon --daemonize

# Background with custom PID file
vfab daemon --daemonize --pid-file /var/run/vfab/vfab.pid
```

### `--user, -u`
**Default:** Current user  
**Description:** Run as specified user (requires root)

**Examples:**
```bash
# Run as current user
vfab daemon

# Run as specific user (system-wide installation)
sudo vfab daemon --user vfab

# Run as nobody for security
sudo vfab daemon --user nobody
```

### `--group, -g`
**Default:** Current user's primary group  
**Description:** Run as specified group (requires root)

**Examples:**
```bash
# Run as vfab group
sudo vfab daemon --group vfab

# Run as dialout group for device access
sudo vfab daemon --group dialout
```

## Usage Examples

### Basic Development Setup
```bash
# Start daemon for development
vfab daemon --log-level debug

# Start with custom workspace
vfab daemon --workspace ./dev-workspace --log-level debug
```

### Production Deployment
```bash
# Production daemon with all options
sudo vfab daemon \
  --host 0.0.0.0 \
  --port 8766 \
  --workspace /var/lib/vfab/workspace \
  --config /etc/vfab/production.yaml \
  --log-level info \
  --daemonize \
  --pid-file /var/run/vfab/vfab.pid \
  --user vfab \
  --group vfab
```

### Docker/Container Setup
```bash
# Container-friendly daemon
vfab daemon \
  --host 0.0.0.0 \
  --port 8766 \
  --workspace /data/workspace \
  --log-level info
```

### Testing and Debugging
```bash
# Debug mode with verbose logging
vfab daemon --log-level debug --workspace ./test-workspace

# Test configuration
vfab daemon --config ./test-config.yaml --log-level debug
```

## Daemon Lifecycle

### Startup Process
1. **Configuration Loading** - Load and validate configuration
2. **Database Initialization** - Connect to database and run migrations
3. **WebSocket Server** - Start WebSocket server on specified host/port
4. **Hardware Detection** - Initialize and configure plotting devices
5. **Job Queue Processing** - Begin processing queued jobs
6. **Hook System** - Initialize hook execution system

### Runtime Operations
- **Job Processing** - Continuously process job queue
- **WebSocket Broadcasting** - Send real-time updates to clients
- **Device Management** - Monitor and manage hardware devices
- **Health Monitoring** - Track system health and performance
- **Log Rotation** - Manage log files and rotation

### Graceful Shutdown
The daemon handles shutdown signals gracefully:
1. **SIGTERM/SIGINT** - Stop accepting new jobs
2. **Complete Active Jobs** - Finish currently running jobs
3. **WebSocket Cleanup** - Close client connections
4. **Hardware Shutdown** - Safely power down devices
5. **Database Cleanup** - Close database connections
6. **PID File Removal** - Remove PID file if created

## Process Management

### Systemd Service
```ini
# /etc/systemd/system/vfab.service
[Unit]
Description=vfab Daemon
After=network.target

[Service]
Type=simple
User=vfab
Group=vfab
ExecStart=/usr/bin/vfab daemon \
  --host 0.0.0.0 \
  --port 8766 \
  --workspace /var/lib/vfab/workspace \
  --config /etc/vfab/config.yaml \
  --log-level info
PIDFile=/var/run/vfab/vfab.pid
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Service Management
```bash
# Enable and start service
sudo systemctl enable vfab
sudo systemctl start vfab

# Check status
sudo systemctl status vfab

# View logs
sudo journalctl -u vfab -f

# Restart service
sudo systemctl restart vfab

# Stop service
sudo systemctl stop vfab
```

### OpenRC Service (Gentoo/Alpine)
```bash
#!/sbin/openrc-run
# /etc/init.d/vfab

command="/usr/bin/vfab daemon"
command_args="--host 0.0.0.0 --port 8766 --workspace /var/lib/vfab/workspace"
command_user="vfab"
command_group="vfab"
pidfile="/var/run/vfab/vfab.pid"
command_background="true"

depend() {
    need net
    after firewall
}
```

## Configuration Integration

The daemon integrates with several configuration sections:

### WebSocket Configuration
```yaml
websocket:
  enabled: true
  host: "localhost"
  port: 8766
  authenticate: false
  api_key: null
  max_connections: 100
  heartbeat_interval: 30
```

### Database Configuration
```yaml
database:
  url: "sqlite:///workspace/vfab.db"
  pool_size: 10
  max_overflow: 20
```

### Device Configuration
```yaml
device:
  type: "axidraw"
  port: "/dev/ttyUSB0"
  baud_rate: 9600
  timeout: 30
```

### Logging Configuration
```yaml
logging:
  level: "info"
  file: "workspace/logs/vfab.log"
  max_size: "10MB"
  backup_count: 5
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Monitoring and Observability

### Health Endpoints
The daemon provides health information via multiple channels:

#### WebSocket Health
```javascript
// Subscribe to system channel for health updates
ws.send(JSON.stringify({
  type: 'SUBSCRIBE',
  channels: ['system']
}));

// Receive health status
{
  "type": "system_status",
  "timestamp": "2025-11-12T19:30:00Z",
  "status": "healthy",
  "uptime": 86400,
  "active_jobs": 2,
  "queue_length": 5,
  "memory_usage": 0.65,
  "cpu_usage": 0.23
}
```

#### Process Monitoring
```bash
# Check if daemon is running
ps aux | grep vfab

# Check WebSocket connections
netstat -an | grep 8766

# Monitor resource usage
top -p $(cat /var/run/vfab/vfab.pid)
```

#### Log Monitoring
```bash
# Follow daemon logs
tail -f /var/lib/vfab/workspace/logs/vfab.log

# Systemd logs
sudo journalctl -u vfab -f

# Filter for WebSocket events
grep "websocket" /var/lib/vfab/workspace/logs/vfab.log
```

## Performance Tuning

### Memory Optimization
```yaml
# Configuration for memory efficiency
database:
  pool_size: 5          # Reduce connection pool
  max_overflow: 10       # Limit overflow connections

websocket:
  max_connections: 50    # Limit concurrent connections
  heartbeat_interval: 60 # Increase heartbeat interval
```

### CPU Optimization
```bash
# Set process priority
vfab daemon --nice 10

# Limit CPU usage (requires cpulimit)
cpulimit -l 50 -p $(cat /var/run/vfab/vfab.pid) &
```

### I/O Optimization
```yaml
logging:
  level: "warning"       # Reduce log volume
  max_size: "50MB"      # Larger log files
  backup_count: 3        # Fewer backups
```

## Troubleshooting

### Common Issues

**Daemon Won't Start**
```bash
# Check configuration
vfab check config

# Check database access
vfab check database

# Check permissions
ls -la /var/lib/vfab/workspace
```

**WebSocket Connection Issues**
```bash
# Check if port is available
netstat -tlnp | grep 8766

# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     http://localhost:8766/ws
```

**Permission Issues**
```bash
# Check user permissions
id vfab

# Check device access
ls -la /dev/ttyUSB*

# Fix device permissions
sudo usermod -a -G dialout vfab
```

### Debug Mode
```bash
# Enable comprehensive debugging
vfab daemon \
  --log-level debug \
  --workspace ./debug-workspace \
  --config ./debug-config.yaml
```

### Log Analysis
```bash
# Error analysis
grep "ERROR" /var/lib/vfab/workspace/logs/vfab.log

# WebSocket connection analysis
grep "websocket" /var/lib/vfab/workspace/logs/vfab.log

# Performance analysis
grep "performance" /var/lib/vfab/workspace/logs/vfab.log
```

## Security Considerations

### Network Security
- **Firewall Configuration** - Restrict access to WebSocket port
- **SSL/TLS** - Use reverse proxy with SSL termination
- **Authentication** - Enable API key authentication
- **Rate Limiting** - Configure connection limits

### Process Security
- **User Isolation** - Run as dedicated non-root user
- **File Permissions** - Restrict workspace and config access
- **Resource Limits** - Set memory and CPU limits
- **Audit Logging** - Enable comprehensive logging

### Example Security Configuration
```yaml
websocket:
  authenticate: true
  api_key: "your-secret-api-key"
  max_connections: 10
  allowed_origins: ["https://your-domain.com"]

logging:
  level: "info"
  audit: true
  security_events: true
```

The vfab daemon provides a robust, production-ready foundation for automated plotting operations with comprehensive monitoring and management capabilities.