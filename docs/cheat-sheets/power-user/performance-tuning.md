# Performance Tuning Cheat Sheet

## **System Performance Analysis**

### **Benchmark Your Setup**
```bash
# Run comprehensive performance benchmark
plotty benchmark --full

# Test plotting speed with sample design
plotty add --benchmark --sample complex_test.svg

# Analyze system resources
plotty system stats --detailed
```

### **Identify Bottlenecks**
```bash
# Check CPU usage during plotting
top -p $(pgrep plottyd)

# Monitor memory usage
plotty system memory --watch

# Analyze I/O performance
iostat -x 1 10  # During plotting operation

# Check for thermal throttling
sensors | grep -E "(Core|temp)"
```

## **ploTTY Configuration Optimization**

### **Performance-Focused Config**
```yaml
# config/performance.yaml
plotting:
  # Speed optimizations
  acceleration: 1.5
  corner_speed: 0.8
  straight_speed: 1.2
  
  # Quality vs speed balance
  precision: medium
  smoothing: enabled
  
  # Memory management
  buffer_size: 64MB
  cache_paths: true
  
system:
  # Resource allocation
  max_memory_usage: 2GB
  cpu_priority: high
  
  # Parallel processing
  worker_threads: 4
  parallel_processing: true
  
database:
  # Performance settings
  connection_pool: 10
  query_cache: 100MB
  batch_size: 50
```

### **Apply Performance Config**
```bash
# Test performance config
plotty --config config/performance.yaml check system.svg

# Benchmark difference
plotty benchmark --config config/performance.yaml
plotty benchmark --config config/default.yaml

# Set as default for production
cp config/performance.yaml config/config.yaml
```

## **Hardware Optimization**

### **Plotter Hardware Tuning**
```bash
# Optimize AxiDraw settings
plotty hardware axidraw tune --speed-test

# Set optimal speed for your paper/pen combo
plotty hardware axidraw preset --paper premium --pen fine

# Calibrate for precision vs speed
plotty hardware calibrate --mode speed

# Test different acceleration profiles
for accel in 1.0 1.2 1.5 2.0; do
    echo "Testing acceleration: $accel"
    plotty add --acceleration $accel test_pattern.svg
    plotty resume
    plotty wait
done
```

### **Pen and Paper Optimization**
```bash
# Find optimal pen pressure
plotty tune pen-pressure --range 20-60 --step 5

# Test different pen speeds for paper type
plotty tune pen-speed --paper premium --pen fine

# Create material-specific presets
plotty preset create --name "fast_draft" --speed 60 --force 30
plotty preset create --name "quality_final" --speed 25 --force 45
```

## **Memory and Storage Optimization**

### **Memory Usage Monitoring**
```python
# memory_monitor.py
import psutil
import time
import subprocess
from pathlib import Path

class MemoryMonitor:
    def __init__(self):
        self.process_name = "plottyd"
        self.log_file = "performance/memory_usage.log"
        Path("performance").mkdir(exist_ok=True)
    
    def monitor_memory(self, duration=300, interval=5):
        """Monitor memory usage during plotting"""
        start_time = time.time()
        
        with open(self.log_file, 'w') as f:
            f.write("timestamp,memory_mb,cpu_percent\n")
            
            while time.time() - start_time < duration:
                # Find ploTTY process
                for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                    if proc.info['name'] == self.process_name:
                        memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                        cpu_percent = proc.info['cpu_percent']
                        
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"{timestamp},{memory_mb:.1f},{cpu_percent:.1f}\n")
                        f.flush()
                        
                        print(f"Memory: {memory_mb:.1f}MB, CPU: {cpu_percent:.1f}%")
                        break
                
                time.sleep(interval)
    
    def analyze_memory_patterns(self):
        """Analyze memory usage patterns"""
        if not Path(self.log_file).exists():
            print("No memory log found. Run monitor_memory() first.")
            return
        
        # Simple analysis
        with open(self.log_file) as f:
            lines = f.readlines()[1:]  # Skip header
        
        memory_values = []
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) >= 2:
                memory_values.append(float(parts[1]))
        
        if memory_values:
            avg_memory = sum(memory_values) / len(memory_values)
            max_memory = max(memory_values)
            min_memory = min(memory_values)
            
            print(f"Memory Analysis:")
            print(f"  Average: {avg_memory:.1f}MB")
            print(f"  Peak: {max_memory:.1f}MB")
            print(f"  Minimum: {min_memory:.1f}MB")
            print(f"  Range: {max_memory - min_memory:.1f}MB")

# Usage
if __name__ == "__main__":
    monitor = MemoryMonitor()
    
    # Monitor during a plotting job
    print("Starting memory monitor for 5 minutes...")
    monitor.monitor_memory(duration=300, interval=2)
    
    # Analyze results
    monitor.analyze_memory_patterns()
```

### **Storage Performance**
```bash
# Test disk I/O performance
dd if=/dev/zero of=performance/test_file bs=1M count=100 oflag=direct
dd if=performance/test_file of=/dev/null bs=1M iflag=direct

# Optimize database location (use SSD if available)
sudo systemctl stop plottyd
sudo mv /var/lib/plotty /ssd/plotty
sudo ln -s /ssd/plotty /var/lib/plotty
sudo systemctl start plottyd

# Check database performance
plotty db benchmark --operations 1000
```

## **Network Optimization**

### **Remote ploTTY Setup**
```bash
# Optimize for remote access
plotty config set network.buffer_size 1MB
plotty config set network.compression true
plotty config set network.timeout 30s

# Test network latency
ping -c 10 plotter-server.local

# Test file transfer speed
scp large_design.svg plotter-server.local:/tmp/
time plotty --host plotter-server.local add /tmp/large_design.svg
```

### **Caching Strategies**
```yaml
# config/network_cache.yaml
cache:
  # File caching
  enable_file_cache: true
  cache_directory: /tmp/plotty_cache
  max_cache_size: 1GB
  
  # Path optimization cache
  path_cache: true
  optimization_cache_duration: 24h
  
  # Preview cache
  preview_cache: true
  preview_resolution: medium
```

## **Batch Processing Optimization**

### **Parallel Job Processing**
```python
# parallel_optimizer.py
import multiprocessing as mp
import subprocess
import time
from pathlib import Path

class BatchOptimizer:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or mp.cpu_count() - 1
    
    def optimize_single_file(self, file_path):
        """Optimize single file for faster plotting"""
        output_path = file_path.parent / f"optimized_{file_path.name}"
        
        # Use vpype for optimization
        cmd = [
            'vpype', 'read', str(file_path),
            'linemerge', '--tolerance', '0.3mm',
            'linesort',
            'simplify', '--tolerance', '0.2mm',
            'write', str(output_path)
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        return {
            'input_file': str(file_path),
            'output_file': str(output_path),
            'processing_time': end_time - start_time,
            'success': result.returncode == 0,
            'size_reduction': self.calculate_size_reduction(file_path, output_path)
        }
    
    def calculate_size_reduction(self, input_file, output_file):
        """Calculate file size reduction"""
        input_size = input_file.stat().st_size
        output_size = output_file.stat().st_size
        return (input_size - output_size) / input_size * 100
    
    def optimize_batch(self, input_dir, output_dir):
        """Optimize batch of files in parallel"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Get all SVG files
        svg_files = list(input_path.glob("*.svg"))
        
        print(f"Optimizing {len(svg_files)} files using {self.max_workers} workers...")
        
        # Process in parallel
        with mp.Pool(self.max_workers) as pool:
            results = pool.map(self.optimize_single_file, svg_files)
        
        # Generate report
        total_time = sum(r['processing_time'] for r in results)
        avg_reduction = sum(r['size_reduction'] for r in results) / len(results)
        
        print(f"Batch optimization complete:")
        print(f"  Total processing time: {total_time:.1f}s")
        print(f"  Average file size reduction: {avg_reduction:.1f}%")
        print(f"  Files processed: {len(results)}")
        
        return results

# Usage
if __name__ == "__main__":
    optimizer = BatchOptimizer(max_workers=4)
    results = optimizer.optimize_batch("designs/raw", "designs/optimized")
```

## **Advanced Performance Tuning**

### **Custom Optimization Profiles**
```yaml
# config/profiles/speed.yaml
plotting:
  speed: 80
  acceleration: 2.0
  precision: low
  smoothing: minimal

# config/profiles/quality.yaml  
plotting:
  speed: 30
  acceleration: 1.0
  precision: high
  smoothing: maximum

# config/profiles/balanced.yaml
plotting:
  speed: 50
  acceleration: 1.5
  precision: medium
  smoothing: standard
```

### **Profile Switching Script**
```bash
#!/bin/bash
# switch_profile.sh

switch_profile() {
    local profile=$1
    
    echo "Switching to $profile profile..."
    
    # Backup current config
    cp config/config.yaml config/config_backup_$(date +%Y%m%d_%H%M%S).yaml
    
    # Apply new profile
    cp "config/profiles/$profile.yaml" config/config.yaml
    
    # Restart ploTTY with new config
    sudo systemctl restart plottyd
    
    # Verify new settings
    sleep 3
    plotty config show | grep -E "(speed|acceleration|precision)"
    
    echo "Profile switch complete"
}

# Usage
# switch_profile speed
# switch_profile quality
# switch_profile balanced
```

### **Real-time Performance Monitoring**
```python
# realtime_monitor.py
import psutil
import time
import json
from datetime import datetime

class RealtimeMonitor:
    def __init__(self):
        self.metrics = []
        self.monitoring = False
    
    def start_monitoring(self):
        """Start real-time performance monitoring"""
        self.monitoring = True
        
        while self.monitoring:
            timestamp = datetime.now().isoformat()
            
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # ploTTY specific metrics
            plotty_memory = 0
            plotty_cpu = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                if proc.info['name'] == 'plottyd':
                    plotty_memory = proc.info['memory_info'].rss / 1024 / 1024
                    plotty_cpu = proc.info['cpu_percent']
                    break
            
            metric = {
                'timestamp': timestamp,
                'system_cpu': cpu_percent,
                'system_memory': memory.percent,
                'plotty_memory_mb': plotty_memory,
                'plotty_cpu': plotty_cpu,
                'disk_free_gb': disk.free / 1024 / 1024 / 1024
            }
            
            self.metrics.append(metric)
            
            # Display current metrics
            print(f"\rCPU: {cpu_percent:5.1f}% | "
                  f"Memory: {memory.percent:5.1f}% | "
                  f"ploTTY: {plotty_memory:6.1f}MB | "
                  f"Disk: {disk.free/1024/1024/1024:6.1f}GB free", end='')
            
            time.sleep(2)
    
    def stop_monitoring(self):
        """Stop monitoring and save results"""
        self.monitoring = False
        print("\nMonitoring stopped")
        
        # Save metrics to file
        with open(f"performance/metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"Saved {len(self.metrics)} data points")
    
    def analyze_performance(self):
        """Analyze collected performance data"""
        if not self.metrics:
            print("No performance data to analyze")
            return
        
        # Calculate averages
        avg_cpu = sum(m['system_cpu'] for m in self.metrics) / len(self.metrics)
        avg_memory = sum(m['system_memory'] for m in self.metrics) / len(self.metrics)
        avg_plotty_memory = sum(m['plotty_memory_mb'] for m in self.metrics) / len(self.metrics)
        
        # Find peaks
        max_cpu = max(m['system_cpu'] for m in self.metrics)
        max_memory = max(m['system_memory'] for m in self.metrics)
        max_plotty_memory = max(m['plotty_memory_mb'] for m in self.metrics)
        
        print(f"\nPerformance Analysis:")
        print(f"  Average CPU: {avg_cpu:.1f}% (Peak: {max_cpu:.1f}%)")
        print(f"  Average Memory: {avg_memory:.1f}% (Peak: {max_memory:.1f}%)")
        print(f"  Average ploTTY Memory: {avg_plotty_memory:.1f}MB (Peak: {max_plotty_memory:.1f}MB)")

# Usage
if __name__ == "__main__":
    monitor = RealtimeMonitor()
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        monitor.analyze_performance()
```

## **Troubleshooting Performance Issues**

### **Common Performance Problems**
```bash
# Check for memory leaks
plotty system memory --leak-detection

# Identify slow operations
plotty debug --profile slow_operation.svg

# Check database performance
plotty db analyze --slow-queries

# Test with different configurations
for config in speed balanced quality; do
    echo "Testing $config profile..."
    time plotty --config config/profiles/$config.yaml add test.svg
done
```

### **Performance Recovery**
```bash
# Clear caches if memory is high
plotty cache clear --all

# Restart services if performance degrades
sudo systemctl restart plottyd

# Optimize database
plotty db optimize --full

# Reset to defaults if needed
plotty config reset --performance
```

## **Related Cheat Sheets**
- [Studio Management](studio-management.md) - Overall studio optimization
- [Batch Production](batch-production.md) - High-volume workflows
- [Configuration Reference](../reference/configuration.md) - All configuration options

## **Performance Tuning Tips**
- **Benchmark first**: Always measure before and after changes
- **Change one thing at a time**: Isolate the effect of each optimization
- **Monitor continuously**: Use real-time monitoring during production
- **Balance speed vs quality**: Find the right compromise for your use case
- **Document settings**: Keep track of what works best for different scenarios