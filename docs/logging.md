# ploTTY Logging Guide

## Overview

ploTTY uses structured logging that writes to `~/.local/share/plotty/logs/plotty.log` by default. Instead of custom CLI commands, we recommend using standard Unix/Linux tools for log management.

## Log Configuration

Logging is configured in `config.yaml`:

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "$XDG_DATA_HOME/plotty/logs/plotty.log"
```

## External Log Management Tools

### Basic Log Viewing

```bash
# Follow logs in real-time
tail -f ~/.local/share/plotty/logs/plotty.log

# View last 100 lines
tail -n 100 ~/.local/share/plotty/logs/plotty.log

# Search for errors
grep "ERROR" ~/.local/share/plotty/logs/plotty.log

# Search for specific job
grep "job_abc123" ~/.local/share/plotty/logs/plotty.log
```

### System Logging (Recommended)

If running as a systemd service, logs are also available via journalctl:

```bash
# View ploTTY logs
journalctl -u plotty -f

# Filter by error level
journalctl -u plotty -p err

# Since last boot
journalctl -u plotty -b

# Last 100 lines
journalctl -u plotty -n 100
```

### Log Rotation

Use `logrotate` for automatic log management:

```bash
# Create logrotate config
sudo tee /etc/logrotate.d/plotty << EOF
~/.local/share/plotty/logs/plotty.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 $USER $USER
}
EOF

# Test logrotate
logrotate -d /etc/logrotate.d/plotty
```

### Advanced Log Analysis

#### Using `awk` for statistics:
```bash
# Count log levels
awk '{print $3}' ~/.local/share/plotty/logs/plotty.log | sort | uniq -c

# Extract timestamps for analysis
awk '{print $1, $2}' ~/.local/share/plotty/logs/plotty.log
```

#### Using `sed` for cleanup:
```bash
# Remove sensitive information
sed -i 's/password=[^ ]*/password=***/g' ~/.local/share/plotty/logs/plotty.log
```

## Log Formats

ploTTY supports multiple log formats configured in the core logging system:

- **Simple**: Basic timestamp-level-message format
- **Detailed**: Includes module and function information  
- **JSON**: Structured logs for programmatic processing
- **Rich**: Formatted output with colors and styling

## Troubleshooting

### Common Issues

1. **No log file found**
   - Check config.yaml file path
   - Ensure directory exists: `mkdir -p ~/.local/share/plotty/logs`
   - Check permissions

2. **Permission denied**
   ```bash
   # Fix log directory permissions
   mkdir -p ~/.local/share/plotty/logs
   chmod 755 ~/.local/share/plotty/logs
   ```

3. **Logs not updating**
   - Check log level (DEBUG shows most, CRITICAL shows least)
   - Verify ploTTY is actually running
   - Check for disk space

### Log Levels Explained

- **DEBUG**: Detailed diagnostic information
- **INFO**: General information about normal operation
- **WARNING**: Something unexpected happened, but system is working
- **ERROR**: Something failed, but system can continue
- **CRITICAL**: Serious error, system may not continue

## Integration with Monitoring Tools

### Promtail + Grafana
```yaml
# promtail-config.yml
scrape_configs:
  - job_name: plotty
    static_configs:
      - targets:
          - localhost
        labels:
          job: plotty
          __path__: /home/user/.local/share/plotty/logs/plotty.log
```

### Fluentd
```ruby
# fluentd.conf
<source>
  @type tail
  path /home/user/.local/share/plotty/logs/plotty.log
  pos_file /var/log/fluentd/plotty.log.pos
  tag plotty
  format none
</source>
```

## Migration from CLI Commands

Previous CLI commands and their equivalents:

| Old Command | External Tool Equivalent |
|-------------|----------------------|
| `plotty system logs list` | `ls -la ~/.local/share/plotty/logs/` |
| `plotty system logs show` | `tail -f ~/.local/share/plotty/logs/plotty.log` |
| `plotty system logs cleanup` | `find ~/.local/share/plotty/logs -name "*.log.*" -mtime +30 -delete` |

This approach provides more flexibility and better integration with existing system administration tools.