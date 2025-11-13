# Real-Time Monitoring Cheat Sheet

## 🧭 Quick Navigation
- **Daemon setup?** [Daemon Reference](../api/daemon-reference.md)
- **WebSocket API?** [WebSocket Monitoring](../api/websocket-monitoring.md)
- **Configuration help?** [Configuration Reference](../reference/configuration.md)
- **Troubleshooting?** [Troubleshooting Basics](../beginner/troubleshooting-basics.md)

---

## **WebSocket Monitoring Quick Start**

### **Basic Monitoring Setup**
```bash
# 1. Start ploTTY daemon
plotty daemon --log-level info

# 2. Monitor all activity (new terminal)
plotty monitor --follow

# 3. Monitor specific job
plotty monitor --job-id my_design_001 --follow
```

### **Production Monitoring**
```bash
# Start daemon with production settings
sudo plotty daemon \
  --host 0.0.0.0 \
  --port 8766 \
  --log-level info \
  --daemonize

# Remote monitoring
plotty monitor \
  --host monitor.example.com \
  --api-key your-secret-key \
  --follow
```

---

## **Real-Time Dashboard Setup**

### **Simple Terminal Dashboard**
```python
# dashboard.py
import asyncio
import json
from datetime import datetime
import sys

async def simple_dashboard():
    import websockets
    
    uri = "ws://localhost:8766/ws"
    async with websockets.connect(uri) as websocket:
        # Subscribe to all channels
        await websocket.send(json.dumps({
            "type": "SUBSCRIBE",
            "channels": ["jobs", "system", "device"]
        }))
        
        print("🔌 Connected to ploTTY WebSocket")
        print("=" * 60)
        
        async for message in websocket:
            data = json.loads(message)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if data['type'] == 'job_state_change':
                job_id = data['job_id']
                from_state = data['from_state']
                to_state = data['to_state']
                print(f"[{timestamp}] 📋 Job {job_id}: {from_state} → {to_state}")
                
            elif data['type'] == 'job_progress':
                job_id = data['job_id']
                progress = data['progress'] * 100
                print(f"[{timestamp}] 📊 Job {job_id}: {progress:.1f}% complete")
                
            elif data['type'] == 'system_alert':
                level = data['level']
                message = data['message']
                icon = "🚨" if level == 'error' else "⚠️"
                print(f"[{timestamp}] {icon} {level.upper()}: {message}")

if __name__ == "__main__":
    try:
        asyncio.run(simple_dashboard())
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
```

### **Web Dashboard (HTML/JavaScript)**
```html
<!-- dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>ploTTY Real-Time Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status { padding: 10px; margin: 5px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .warning { background: #fff3cd; color: #856404; }
        .error { background: #f8d7da; color: #721c24; }
        .job { border-left: 4px solid #007bff; padding-left: 10px; }
        .system { border-left: 4px solid #28a745; padding-left: 10px; }
        .device { border-left: 4px solid #ffc107; padding-left: 10px; }
    </style>
</head>
<body>
    <h1>🔌 ploTTY Real-Time Monitor</h1>
    <div id="status">🔄 Connecting...</div>
    <div id="messages"></div>

    <script>
        const ws = new WebSocket('ws://localhost:8766/ws');
        const statusDiv = document.getElementById('status');
        const messagesDiv = document.getElementById('messages');
        
        ws.onopen = () => {
            statusDiv.innerHTML = '✅ Connected to ploTTY';
            statusDiv.className = 'status success';
            
            // Subscribe to all channels
            ws.send(JSON.stringify({
                type: 'SUBSCRIBE',
                channels: ['jobs', 'system', 'device']
            }));
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const timestamp = new Date().toLocaleTimeString();
            
            let messageClass = 'status';
            let icon = '📋';
            
            if (data.type === 'job_state_change') {
                messageClass += ' job';
                icon = '📋';
            } else if (data.type === 'system_alert') {
                messageClass += ' system';
                icon = data.level === 'error' ? '🚨' : '⚠️';
            } else if (data.type === 'device_status') {
                messageClass += ' device';
                icon = '🔧';
            }
            
            const messageDiv = document.createElement('div');
            messageDiv.className = messageClass;
            messageDiv.innerHTML = `
                <strong>[${timestamp}] ${icon}</strong> ${data.type}<br>
                <small>${JSON.stringify(data, null, 2)}</small>
            `;
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        };
        
        ws.onclose = () => {
            statusDiv.innerHTML = '❌ Disconnected from ploTTY';
            statusDiv.className = 'status error';
        };
        
        ws.onerror = (error) => {
            statusDiv.innerHTML = '🚨 Connection error';
            statusDiv.className = 'status error';
            console.error('WebSocket error:', error);
        };
    </script>
</body>
</html>
```

---

## **Channel-Specific Monitoring**

### **Job Monitoring Only**
```bash
# Monitor job state changes
plotty monitor --channels jobs --follow

# Monitor specific job progress
plotty monitor --channels jobs --job-id batch_job_001 --follow

# JSON output for automation
plotty monitor --channels jobs --format json --follow
```

### **System Status Monitoring**
```bash
# System alerts and status
plotty monitor --channels system --follow

# Filter for errors only
plotty monitor --channels system --level error --follow
```

### **Device Monitoring**
```bash
# Hardware status updates
plotty monitor --channels device --follow

# Device status with JSON parsing
plotty monitor --channels device --format json | jq '.status'
```

---

## **Automation & Integration**

### **Alert System Integration**
```python
# alert_bot.py
import asyncio
import websockets
import json
import smtplib
from email.mime.text import MIMEText

class AlertBot:
    def __init__(self, email_config, webhook_url=None):
        self.email_config = email_config
        self.webhook_url = webhook_url
        
    async def monitor(self):
        import websockets
        
        uri = "ws://localhost:8766/ws"
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({
                "type": "SUBSCRIBE",
                "channels": ["system"]
            }))
            
            async for message in ws:
                data = json.loads(message)
                
                if data['type'] == 'system_alert':
                    await self.handle_alert(data)
    
    async def handle_alert(self, alert):
        level = alert['level']
        message = alert['message']
        
        if level in ['error', 'critical']:
            await self.send_email_alert(alert)
            if self.webhook_url:
                await self.send_webhook_alert(alert)
    
    async def send_email_alert(self, alert):
        msg = MIMEText(f"ploTTY Alert: {alert['message']}")
        msg['Subject'] = f"🚨 ploTTY {alert['level'].upper()}"
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']
        
        # Send email (implementation depends on your SMTP server)
        # smtp.send_message(msg)
        print(f"📧 Email alert sent: {alert['message']}")
    
    async def send_webhook_alert(self, alert):
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "text": f"🚨 ploTTY {alert['level'].upper()}: {alert['message']}",
                "username": "ploTTY Bot"
            }
            
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status == 200:
                    print(f"📱 Webhook alert sent: {alert['message']}")

# Usage
alert_bot = AlertBot(
    email_config={
        'from': 'plotty@studio.com',
        'to': 'admin@studio.com'
    },
    webhook_url='https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
)

asyncio.run(alert_bot.monitor())
```

### **Job Progress Tracking**
```python
# progress_tracker.py
import asyncio
import json
import time
from datetime import datetime

class JobProgressTracker:
    def __init__(self):
        self.active_jobs = {}
        self.start_times = {}
        
    async def track(self):
        import websockets
        
        uri = "ws://localhost:8766/ws"
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({
                "type": "SUBSCRIBE",
                "channels": ["jobs"]
            }))
            
            async for message in ws:
                data = json.loads(message)
                await self.update_job_progress(data)
    
    async def update_job_progress(self, data):
        job_id = data['job_id']
        timestamp = datetime.now()
        
        if data['type'] == 'job_state_change':
            if data['to_state'] == 'RUNNING':
                self.start_times[job_id] = timestamp
                print(f"▶️  Job {job_id} started at {timestamp.strftime('%H:%M:%S')}")
                
            elif data['to_state'] in ['COMPLETED', 'FAILED']:
                if job_id in self.start_times:
                    start_time = self.start_times[job_id]
                    duration = timestamp - start_time
                    print(f"⏹️  Job {job_id} {data['to_state'].lower()} after {duration}")
                    del self.start_times[job_id]
                    
        elif data['type'] == 'job_progress':
            progress = data['progress'] * 100
            remaining = data.get('estimated_remaining', 0)
            print(f"📊 Job {job_id}: {progress:.1f}% complete (~{remaining}s remaining)")

tracker = JobProgressTracker()
asyncio.run(tracker.track())
```

---

## **Production Monitoring Patterns**

### **Multi-Instance Monitoring**
```bash
#!/bin/bash
# monitor_multiple.sh

INSTANCES=("localhost:8766" "production.example.com:8766" "backup.example.com:8766")

for instance in "${INSTANCES[@]}"; do
    host=$(echo $instance | cut -d: -f1)
    port=$(echo $instance | cut -d: -f2)
    
    echo "🔌 Monitoring $instance..."
    plotty monitor \
      --host $host \
      --port $port \
      --format json \
      --follow \
      > "monitor_${host}_${port}.log" &
done

echo "📊 Monitoring all instances..."
wait
```

### **Health Check Automation**
```python
# health_monitor.py
import asyncio
import json
import time
from datetime import datetime, timedelta

class HealthMonitor:
    def __init__(self):
        self.last_heartbeat = {}
        self.job_counts = {}
        
    async def monitor_health(self):
        import websockets
        
        uri = "ws://localhost:8766/ws"
        try:
            async with websockets.connect(uri) as ws:
                await ws.send(json.dumps({
                    "type": "SUBSCRIBE",
                    "channels": ["system"]
                }))
                
                async for message in ws:
                    data = json.loads(message)
                    
                    if data['type'] == 'system_status':
                        self.check_system_health(data)
                    elif data['type'] == 'system_alert':
                        self.handle_health_alert(data)
                        
        except Exception as e:
            print(f"❌ Health monitor failed: {e}")
    
    def check_system_health(self, status):
        uptime = status.get('uptime', 0)
        active_jobs = status.get('active_jobs', 0)
        queue_length = status.get('queue_length', 0)
        
        # Health checks
        if uptime < 60:  # Less than 1 minute
            print("⚠️  System recently restarted")
        
        if active_jobs > 10:
            print("⚠️  High job load detected")
        
        if queue_length > 50:
            print("⚠️  Large job queue")
        
        print(f"✅ System healthy: {uptime}s uptime, {active_jobs} active jobs, {queue_length} queued")
    
    def handle_health_alert(self, alert):
        level = alert['level']
        message = alert['message']
        
        if level == 'critical':
            print(f"🚨 CRITICAL: {message}")
        elif level == 'error':
            print(f"❌ ERROR: {message}")
        elif level == 'warning':
            print(f"⚠️  WARNING: {message}")

monitor = HealthMonitor()
asyncio.run(monitor.monitor_health())
```

---

## **Troubleshooting WebSocket Issues**

### **Connection Problems**
```bash
# Check if daemon is running
ps aux | grep plotty

# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8766/ws

# Check port availability
netstat -tlnp | grep 8766
```

### **Authentication Issues**
```bash
# Test with API key
plotty monitor --api-key your-key --follow

# Check configuration
plotty info system | grep -i websocket
```

### **Performance Issues**
```bash
# Monitor message rate
plotty monitor --format json --follow | pv -l > /dev/null

# Check connection count
ss -tn state established '( dport = :8766 )' | wc -l

# Monitor daemon resources
top -p $(pgrep -f "plotty daemon")
```

---

## **Configuration Templates**

### **Development WebSocket Config**
```yaml
# config/development.yaml
websocket:
  enabled: true
  host: "localhost"
  port: 8766
  authenticate: false
  max_connections: 10
  heartbeat_interval: 15
  channels: ["jobs", "system", "device"]
  message_rate_limit: 200
  connection_timeout: 300
  compression: true

logging:
  level: "debug"
  modules: ["plotty.websocket"]
```

### **Production WebSocket Config**
```yaml
# config/production.yaml
websocket:
  enabled: true
  host: "0.0.0.0"
  port: 8766
  authenticate: true
  api_key: "${PLOTTY_API_KEY}"
  max_connections: 50
  heartbeat_interval: 60
  channels: ["jobs", "system", "device"]
  allowed_origins:
    - "https://monitor.example.com"
    - "https://dashboard.example.com"
  message_rate_limit: 100
  connection_timeout: 600
  compression: true

logging:
  level: "info"
  audit: true
  security_events: true
```

### **High-Security Config**
```yaml
# config/high-security.yaml
websocket:
  enabled: true
  host: "127.0.0.1"  # Local only
  port: 8766
  authenticate: true
  api_key: "${PLOTTY_API_KEY}"
  max_connections: 5
  heartbeat_interval: 30
  channels: ["jobs", "system"]  # No device channel
  allowed_origins: ["https://trusted.example.com"]
  message_rate_limit: 30
  connection_timeout: 300
  compression: false  # Disable for security

logging:
  level: "warning"
  audit: true
  security_events: true
  access_log: true
```

This real-time monitoring system provides comprehensive visibility into ploTTY operations, enabling responsive dashboards, automated alerting, and professional studio management.