# Daemon Command Reference

Complete reference for the ploTTY daemon process and WebSocket server.

## Overview

The ploTTY daemon (`plotty daemon`) is a long-running background process that manages:
- Job queue processing and execution
- WebSocket server for real-time monitoring
- Hardware device management
- System state coordination

## Command Syntax

```bash
plotty daemon [OPTIONS]
```

## Options

### `--host, -h`
**Default:** `localhost`  
**Description:** WebSocket server bind address

**Examples:**
```bash
# Bind to localhost (default)
plotty daemon

# Bind to all interfaces
plotty daemon --host 0.0.0.0

# Bind to specific network interface
plotty daemon --host 192.168.1.100
```

### `--port, -p`
**Default:** `8766`  
**Description:** WebSocket server port

**Examples:**
```bash
# Use default port
plotty daemon

# Use custom port
plotty daemon --port 8080

# Use port in production range
plotty daemon --port 8765
```

### `--workspace, -w`
**Default:** `$XDG_DATA_HOME/plotty/workspace`  
**Description:** Working directory for jobs and data

**Examples:**
```bash
# Use default workspace
plotty daemon

# Use custom workspace
plotty daemon --workspace /mnt/storage/plotty-workspace

# Use relative workspace
plotty daemon --workspace ./my-workspace
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
plotty daemon

# Debug mode for troubleshooting
plotty daemon --log-level debug

# Production mode (errors only)
plotty daemon --log-level error
```

### `--config, -c`
**Default:** `$XDG_CONFIG_HOME/plotty/config.yaml`  
**Description:** Path to configuration file

**Examples:**
```bash
# Use default config
plotty daemon

# Use custom config
plotty daemon --config /etc/plotty/production.yaml

# Use project-specific config
plotty daemon --config ./studio-config.yaml
```

### `--pid-file`
**Default:** None  
**Description:** Path to PID file for process management

**Examples:**
```bash
# Create PID file
plotty daemon --pid-file /var/run/plotty/plotty.pid

# Use user-local PID file
plotty daemon --pid-file ~/.local/run/plotty.pid
```

### `--daemonize, -d`
**Default:** `false`  
**Description:** Run as background daemon process

**Examples:**
```bash
# Run in foreground (default)
plotty daemon

# Run as background daemon
plotty daemon --daemonize

# Background with custom PID file
plotty daemon --daemonize --pid-file /var/run/plotty/plotty.pid
```

### `--user, -u`
**Default:** Current user  
**Description:** Run as specified user (requires root)

**Examples:**
```bash
# Run as current user
plotty daemon

# Run as specific user (system-wide installation)
sudo plotty daemon --user plotty

# Run as nobody for security
sudo plotty daemon --user nobody
```

### `--group, -g`
**Default:** Current user's primary group  
**Description:** Run as specified group (requires root)

**Examples:**
```bash
# Run as plotty group
sudo plotty daemon --group plotty

# Run as dialout group for device access
sudo plotty daemon --group dialout
```

## Usage Examples

### Basic Development Setup
```bash
# Start daemon for development
plotty daemon --log-level debug

# Start with custom workspace
plotty daemon --workspace ./dev-workspace --log-level debug
```

### Production Deployment
```bash
# Production daemon with all options
sudo plotty daemon \
  --host 0.0.0.0 \
  --port 8766 \
  --workspace /var/lib/plotty/workspace \
  --config /etc/plotty/production.yaml \
  --log-level info \
  --daemonize \
  --pid-file /var/run/plotty/plotty.pid \
  --user plotty \
  --group plotty
```

### Docker/Container Setup
```bash
# Container-friendly daemon
plotty daemon \
  --host 0.0.0.0 \
  --port 8766 \
  --workspace /data/workspace \
  --log-level info
```

### Testing and Debugging
```bash
# Debug mode with verbose logging
plotty daemon --log-level debug --workspace ./test-workspace

# Test configuration
plotty daemon --config ./test-config.yaml --log-level debug
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
# /etc/systemd/system/plotty.service
[Unit]
Description=ploTTY Daemon
After=network.target

[Service]
Type=simple
User=plotty
Group=plotty
ExecStart=/usr/bin/plotty daemon \
  --host 0.0.0.0 \
  --port 8766 \
  --workspace /var/lib/plotty/workspace \
  --config /etc/plotty/config.yaml \
  --log-level info
PIDFile=/var/run/plotty/plotty.pid
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Service Management
```bash
# Enable and start service
sudo systemctl enable plotty
sudo systemctl start plotty

# Check status
sudo systemctl status plotty

# View logs
sudo journalctl -u plotty -f

# Restart service
sudo systemctl restart plotty

# Stop service
sudo systemctl stop plotty
```

### OpenRC Service (Gentoo/Alpine)
```bash
#!/sbin/openrc-run
# /etc/init.d/plotty

command="/usr/bin/plotty daemon"
command_args="--host 0.0.0.0 --port 8766 --workspace /var/lib/plotty/workspace"
command_user="plotty"
command_group="plotty"
pidfile="/var/run/plotty/plotty.pid"
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
  url: "sqlite:///workspace/plotty.db"
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
  file: "workspace/logs/plotty.log"
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
ps aux | grep plotty

# Check WebSocket connections
netstat -an | grep 8766

# Monitor resource usage
top -p $(cat /var/run/plotty/plotty.pid)
```

#### Log Monitoring
```bash
# Follow daemon logs
tail -f /var/lib/plotty/workspace/logs/plotty.log

# Systemd logs
sudo journalctl -u plotty -f

# Filter for WebSocket events
grep "websocket" /var/lib/plotty/workspace/logs/plotty.log
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
plotty daemon --nice 10

# Limit CPU usage (requires cpulimit)
cpulimit -l 50 -p $(cat /var/run/plotty/plotty.pid) &
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
plotty check config

# Check database access
plotty check database

# Check permissions
ls -la /var/lib/plotty/workspace
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
id plotty

# Check device access
ls -la /dev/ttyUSB*

# Fix device permissions
sudo usermod -a -G dialout plotty
```

### Debug Mode
```bash
# Enable comprehensive debugging
plotty daemon \
  --log-level debug \
  --workspace ./debug-workspace \
  --config ./debug-config.yaml
```

### Log Analysis
```bash
# Error analysis
grep "ERROR" /var/lib/plotty/workspace/logs/plotty.log

# WebSocket connection analysis
grep "websocket" /var/lib/plotty/workspace/logs/plotty.log

# Performance analysis
grep "performance" /var/lib/plotty/workspace/logs/plotty.log
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

The ploTTY daemon provides a robust, production-ready foundation for automated plotting operations with comprehensive monitoring and management capabilities.