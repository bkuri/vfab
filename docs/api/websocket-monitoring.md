# WebSocket Monitoring System

Real-time monitoring and notification system for ploTTY job execution and system state changes.

## Overview

The WebSocket monitoring system provides real-time updates for:
- Job state transitions (FSM changes)
- System status updates
- Device status notifications
- Error and alert messages

## Architecture

```
┌─────────────────┐    WebSocket     ┌─────────────────┐
│   ploTTY Daemon │ ◄──────────────► │  Monitor Client │
│   (WebSocket    │    Messages      │  (Browser/CLI)  │
│    Server)      │                 │                 │
└─────────────────┘                 └─────────────────┘
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│   HookExecutor  │                 │   WebSocket    │
│   (Broadcasts   │                 │   Manager      │
│   State Changes)│                 │   (Routing)    │
└─────────────────┘                 └─────────────────┘
```

## WebSocket Connection

### Connection URL
```
ws://localhost:8766/ws
```

### Authentication
When authentication is enabled, include an API key:
```javascript
const ws = new WebSocket('ws://localhost:8766/ws?api_key=your_api_key');
```

## Message Channels

### Jobs Channel (`jobs`)
Real-time job state changes and progress updates.

#### Message Types

**Job State Change**
```json
{
  "type": "job_state_change",
  "timestamp": "2025-11-12T19:30:00Z",
  "job_id": "my_design_001",
  "from_state": "QUEUED",
  "to_state": "RUNNING",
  "reason": "Job started by daemon",
  "metadata": {
    "pen": "black",
    "paper": "a4",
    "estimated_time": 1800
  }
}
```

**Job Progress**
```json
{
  "type": "job_progress",
  "timestamp": "2025-11-12T19:30:30Z",
  "job_id": "my_design_001",
  "progress": 0.45,
  "current_layer": 2,
  "total_layers": 4,
  "estimated_remaining": 990,
  "metadata": {
    "points_plotted": 1250,
    "total_points": 2780
  }
}
```

### System Channel (`system`)
System status and configuration changes.

#### Message Types

**System Status**
```json
{
  "type": "system_status",
  "timestamp": "2025-11-12T19:30:00Z",
  "status": "ready",
  "daemon_version": "1.1.0",
  "uptime": 3600,
  "active_jobs": 1,
  "queue_length": 3
}
```

**System Alert**
```json
{
  "type": "system_alert",
  "timestamp": "2025-11-12T19:30:00Z",
  "level": "warning",
  "message": "Device temperature high",
  "details": {
    "temperature": 45.2,
    "threshold": 40.0
  }
}
```

### Device Channel (`device`)
Device-specific status and hardware events.

#### Message Types

**Device Status**
```json
{
  "type": "device_status",
  "timestamp": "2025-11-12T19:30:00Z",
  "device_id": "axidraw_001",
  "status": "connected",
  "pen_up": true,
  "position": {
    "x": 150.5,
    "y": 200.2
  },
  "metadata": {
    "firmware_version": "v2.5.3",
    "motor_current": 0.8
  }
}
```

## Client Implementation

### JavaScript (Browser)
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8766/ws');

// Subscribe to channels
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'SUBSCRIBE',
    channels: ['jobs', 'system', 'device']
  }));
};

// Handle messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'job_state_change':
      handleJobStateChange(message);
      break;
    case 'job_progress':
      updateProgressBar(message);
      break;
    case 'system_alert':
      showAlert(message);
      break;
  }
};

function handleJobStateChange(message) {
  console.log(`Job ${message.job_id}: ${message.from_state} → ${message.to_state}`);
  // Update UI elements
}
```

### Python Client
```python
import asyncio
import websockets
import json

async def monitor_plotty():
    uri = "ws://localhost:8766/ws"
    
    async with websockets.connect(uri) as websocket:
        # Subscribe to channels
        subscribe_msg = {
            "type": "SUBSCRIBE",
            "channels": ["jobs", "system"]
        }
        await websocket.send(json.dumps(subscribe_msg))
        
        # Listen for messages
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data['type']}: {data}")
            
            if data['type'] == 'job_state_change':
                print(f"Job {data['job_id']}: {data['from_state']} → {data['to_state']}")

# Run monitor
asyncio.run(monitor_plotty())
```

### CLI Monitor
```bash
# Start built-in monitor
plotty monitor --channels jobs,system

# Monitor with filters
plotty monitor --job-id my_design_001 --level info

# Continuous monitoring
plotty monitor --follow --format json
```

## Configuration

### WebSocket Settings
```yaml
websocket:
  enabled: true                    # Enable WebSocket server
  host: "localhost"              # Server bind address
  port: 8766                    # Server port
  authenticate: false            # Require API key authentication
  api_key: null                 # API key for authentication
  max_connections: 100           # Maximum concurrent connections
  heartbeat_interval: 30         # Heartbeat interval (seconds)
  channels:                     # Available channels
    - "jobs"
    - "system" 
    - "device"
```

### Integration with Hooks
```yaml
hooks:
  RUNNING:
    - command: "echo 'Job started'"
    - websocket: true            # Broadcast to WebSocket clients
  COMPLETED:
    - command: "echo 'Job finished'"
    - websocket: true
  FAILED:
    - command: "echo 'Job failed'"
    - websocket: true
```

## Security Considerations

### Authentication
When `authenticate: true`, clients must provide valid API key:
```javascript
const ws = new WebSocket('ws://localhost:8766/ws?api_key=your_secret_key');
```

### Rate Limiting
The server implements rate limiting to prevent abuse:
- Max 100 messages per minute per connection
- Connection timeout after 5 minutes of inactivity
- Automatic reconnection recommended for clients

### Network Security
- Use WSS (`wss://`) for production deployments
- Configure firewall rules to restrict access
- Consider reverse proxy with SSL termination

## Troubleshooting

### Connection Issues
```bash
# Check if WebSocket server is running
plotty info system | grep websocket

# Test connectivity
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8766/ws
```

### Common Errors

**Connection Refused**
- WebSocket server not running
- Port blocked by firewall
- Incorrect host/port configuration

**Authentication Failed**
- Missing or invalid API key
- Authentication enabled but no key provided

**Message Not Received**
- Not subscribed to correct channel
- Client connection dropped
- Rate limiting in effect

### Debug Mode
Enable debug logging for WebSocket issues:
```yaml
logging:
  level: "debug"
  modules:
    - "plotty.websocket"
```

## Performance

### Optimization Tips
1. **Subscribe to specific channels** - Don't subscribe to all channels if not needed
2. **Use message filtering** - Filter messages client-side to reduce processing
3. **Connection pooling** - Reuse connections for multiple operations
4. **Batch operations** - Group related operations to reduce message overhead

### Monitoring Performance
```bash
# Check WebSocket connection count
plotty stats websocket

# Monitor message throughput
plotty monitor --stats --interval 60
```

## Integration Examples

### Custom Dashboard
```python
# dashboard.py
import asyncio
import websockets
from datetime import datetime

class PlotterDashboard:
    def __init__(self):
        self.jobs = {}
        self.system_status = {}
        
    async def connect(self):
        uri = "ws://localhost:8766/ws"
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({
                "type": "SUBSCRIBE", 
                "channels": ["jobs", "system"]
            }))
            
            async for message in ws:
                data = json.loads(message)
                await self.handle_message(data)
    
    async def handle_message(self, data):
        if data['type'] == 'job_state_change':
            self.update_job_status(data)
        elif data['type'] == 'system_status':
            self.update_system_status(data)
    
    def update_job_status(self, data):
        job_id = data['job_id']
        self.jobs[job_id] = {
            'status': data['to_state'],
            'last_update': datetime.now()
        }
        print(f"Job {job_id}: {data['from_state']} → {data['to_state']}")

dashboard = PlotterDashboard()
asyncio.run(dashboard.connect())
```

### Alert System Integration
```python
# alerts.py
import asyncio
import websockets
import smtplib
from email.mime.text import MIMEText

class AlertManager:
    def __init__(self, email_config):
        self.email_config = email_config
        
    async def monitor_alerts(self):
        uri = "ws://localhost:8766/ws"
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({
                "type": "SUBSCRIBE", 
                "channels": ["system"]
            }))
            
            async for message in ws:
                data = json.loads(message)
                if data['type'] == 'system_alert':
                    await self.send_alert(data)
    
    async def send_alert(self, alert):
        if alert['level'] in ['error', 'critical']:
            await self.email_alert(alert)
    
    async def email_alert(self, alert):
        msg = MIMEText(f"ploTTY Alert: {alert['message']}")
        msg['Subject'] = f"ploTTY {alert['level'].upper()}: {alert['message']}"
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']
        
        # Send email (implementation depends on SMTP server)
        # smtp.send_message(msg)

# Usage
alert_manager = AlertManager({
    'from': 'plotty@studio.com',
    'to': 'admin@studio.com'
})
asyncio.run(alert_manager.monitor_alerts())
```

This WebSocket monitoring system provides real-time visibility into ploTTY operations, enabling responsive user interfaces, automated workflows, and comprehensive system observability.