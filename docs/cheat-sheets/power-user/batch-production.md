# Batch Production Cheat Sheet

**High-volume workflows** - Professional batch processing for maximum efficiency.

---

## 🧭 Quick Navigation
- **New to batch work?** [Multi-Pen Workflow](../creative/multi-pen-workflow.md)
- **Generate designs automatically?** [Batch Art Generation](../creative/batch-art-generation.md)
- **Manage your studio?** [Studio Management](studio-management.md)
- **Optimize performance?** [Performance Tuning](performance-tuning.md)

---

## 🏭 Batch Production Overview

Batch production is perfect for:
- 📦 **Client projects** with multiple designs
- 🎨 **Art editions** and series
- 📋 **Business materials** (cards, letterheads, etc.)
- 🎓 **Educational materials** for workshops
- 🏪 **Product catalogs** and samples

---

## 📋 Project Organization

### Professional Directory Structure
```bash
# Create organized project structure
mkdir -p client_project/{designs,output,documentation,assets}
cd client_project

# Sub-directories for different stages
mkdir -p designs/{raw,approved,final}
mkdir -p output/{proofs,production,archive}
mkdir -p documentation/{specs,reports,invoices}
```

### Batch Import Workflow
```bash
# Import all designs from directory
for file in designs/approved/*.svg; do
    basename=$(basename "$file" .svg)
    vfab add "$file" --name "Client: $basename" --paper a4
done

# Import with metadata
for file in designs/approved/*.svg; do
    basename=$(basename "$file" .svg)
    vfab add "$file" \
        --name "Client: $basename" \
        --paper a4 \
        --priority normal \
        --tags "client,approved,$(date +%Y-%m)"
done
```

### Smart Batch Categorization
```bash
# Categorize by type
vfab add logos/*.svg --name "Client: Logo" --category "logo"
vfab add cards/*.svg --name "Client: Business Card" --category "card"
vfab add letterhead/*.svg --name "Client: Letterhead" --category "letterhead"

# Batch by priority
vfab add urgent/*.svg --priority high
vfab add normal/*.svg --priority normal
vfab add backlog/*.svg --priority low
```

---

## ⚡ Intelligent Batch Planning

### Global Optimization Strategies
```bash
# Plan all jobs with global pen optimization
vfab plan-all --preset fast --optimize-pens --global-pen-order

# Plan by priority
vfab plan-all --priority-order --optimize-pens

# Plan by time constraints
vfab plan-all --max-time-per-job 30m --preset fast
```

### Advanced Planning Options
```bash
# Plan with custom pen order
vfab plan-all --pen-order 2,1,3,4 --minimize-distance

# Plan with quality tiers
vfab plan-all --quality-tiers --auto-preset-selection

# Plan with resource constraints
vfab plan-all --max-pen-changes 50 --max-total-time 4h
```

### Selective Batch Planning
```bash
# Plan specific job categories
vfab plan "Client: Logo*" --preset hq
vfab plan "Client: Business Card*" --preset fast

# Plan by date range
vfab plan --added-after "2025-11-01" --added-before "2025-11-07"

# Plan by complexity
vfab plan-all --complexity-low --preset fast
vfab plan-all --complexity-high --preset hq
```

### Planning Analysis
```bash
# Compare planning strategies
vfab plan-all --preset fast --dry-run --save-as fast_plan
vfab plan-all --preset hq --dry-run --save-as hq_plan
vfab compare fast_plan hq_plan --show-time-estimates

# Analyze planning efficiency
vfab analyze planning --show-bottlenecks --suggest-improvements
```

---

## 🚀 Automated Batch Plotting

### Standard Batch Execution
```bash
# Plot all planned jobs
vfab plot-all

# Plot with safety monitoring
vfab plot-all --preset safe --monitor --auto-retry

# Plot with progress notifications
vfab plot-all --notify-on-complete --notify-on-error
```

### Advanced Batch Plotting
```bash
# Plot with time constraints
vfab plot-all --max-total-time 6h --auto-pause

# Plot with resource management
vfab plot-all --pen-usage-tracking --paper-usage-tracking

# Plot with quality control
vfab plot-all --quality-checks --auto-replot-failed
```

### Conditional Batch Plotting
```bash
# Plot only jobs under time threshold
vfab plot-all --max-job-time 20m

# Plot high-priority jobs first
vfab plot-all --priority-order --skip-low-priority

# Plot with automatic error recovery
vfab plot-all --auto-recovery --max-retries 2
```

### Parallel Processing (Multiple Devices)
```bash
# Distribute across multiple devices
vfab plot-all --devices axidraw_v3_1,axidraw_v3_2 --load-balance

# Device-specific optimization
vfab plot-all --device-1-preset fast --device-2-preset hq

# Monitor multiple devices
vfab monitor --all-devices --consolidated-status
```

---

## 📊 Queue Management & Monitoring

### Real-time Queue Monitoring
```bash
# Live queue monitoring
vfab list queue --watch --refresh 30s

# Detailed queue analysis
vfab list queue --detailed --show-estimates --show-pen-changes

# Queue performance metrics
vfab analyze queue --efficiency --bottlenecks --optimization-suggestions
```

### Intelligent Queue Organization
```bash
# Group jobs by client
vfab queue group --by-client "Acme Corp"

# Reorder by optimization
vfab queue reorder --by-pen-efficiency

# Split large batches
vfab queue split --batch-size 10 --name-suffix "batch_{n}"
```

### Automated Queue Management
```bash
# Smart queue cleanup
vfab queue cleanup --completed --older-than 1d --archive

# Queue optimization
vfab queue optimize --global-pen-order --minimize-total-time

# Queue backup and restore
vfab queue backup --file "queue_backup_$(date +%Y%m%d).json"
vfab queue restore --file "queue_backup_20251107.json"
```

---

## 📈 Production Analytics & Reporting

### Comprehensive Production Reports
```bash
# Daily production summary
vfab report production --date today \
    --include-time-analysis \
    --include-resource-usage \
    --export "production_report_$(date +%Y%m%d).pdf"

# Client-specific reports
vfab report client --name "Acme Corp" \
    --date-range "2025-11-01:2025-11-07" \
    --include-cost-analysis \
    --include-quality-metrics

# Batch performance analysis
vfab analyze batch --name "November Production" \
    --show-efficiency-trends \
    --identify-improvements
```

### Resource Utilization Tracking
```bash
# Pen usage analysis
vfab analyze pens --usage-patterns --wear-analysis --replacement-schedule

# Paper consumption tracking
vfab analyze paper --consumption-by-job --cost-analysis --waste-reduction

# Device performance metrics
vfab analyze devices --uptime --error-rates --maintenance-schedule
```

### Quality Metrics
```bash
# Quality trend analysis
vfab analyze quality --trends --by-pen --by-paper --by-complexity

# Error rate analysis
vfab analyze errors --by-job-type --by-device --by-time-of-day

# Customer satisfaction tracking
vfab analyze satisfaction --by-client --by-job-type --correlate-quality
```

---

## 🤖 Production Automation Scripts

### Daily Production Routine
```bash
#!/bin/bash
# daily_production.sh - Automated daily production

echo "🌅 Starting daily production routine..."

# Morning system check
vfab check ready --detailed
if [ $? -ne 0 ]; then
    echo "❌ System check failed. Aborting production."
    exit 1
fi

# Load today's production schedule
vfab load schedule --file "today/production_schedule.json"

# Optimize for today's constraints
vfab plan-all --optimize-for-today --resource-constraints

# Start production with monitoring
vfab plot-all --monitor --notify-on-complete --auto-recovery

# Generate end-of-day report
vfab report daily --auto-generate --email-studio

echo "✅ Daily production routine complete."
```

### Client Project Automation
```python
#!/usr/bin/env python3
# client_production.py - Automated client project processing

import subprocess
import json
from datetime import datetime

class ClientProduction:
    def __init__(self, client_name):
        self.client_name = client_name
        self.load_client_config()
    
    def load_client_config(self):
        """Load client-specific configuration."""
        with open(f"clients/{self.client_name}/config.json") as f:
            self.config = json.load(f)
    
    def process_project(self):
        """Process entire client project."""
        print(f"🏢 Processing {self.client_name} project...")
        
        # Import designs
        self.import_designs()
        
        # Plan with client standards
        self.plan_production()
        
        # Execute production
        self.execute_production()
        
        # Generate client report
        self.generate_client_report()
    
    def import_designs(self):
        """Import all approved designs."""
        designs = self.config.get('designs', [])
        for design in designs:
            cmd = [
                "vfab", "add", design['file'],
                "--name", f"{self.client_name}: {design['name']}",
                "--paper", design.get('paper', 'a4'),
                "--priority", design.get('priority', 'normal'),
                "--tags", f"client,{self.client_name},{design.get('type', 'general')}"
            ]
            subprocess.run(cmd)
    
    def plan_production(self):
        """Plan production with client-specific settings."""
        # Use client's preferred pen mapping
        pen_mapping = self.config.get('pen_mapping', 'auto')
        
        # Apply client quality standards
        quality_preset = self.config.get('quality_preset', 'hq')
        
        subprocess.run([
            "vfab", "plan-all",
            "--pen-mapping", pen_mapping,
            "--preset", quality_preset,
            "--client-standards", self.client_name
        ])
    
    def execute_production(self):
        """Execute production with client monitoring."""
        subprocess.run([
            "vfab", "plot-all",
            "--monitor", "--quality-checks",
            "--notify-client", self.config.get('notify_email'),
            "--document-for-client"
        ])
    
    def generate_client_report(self):
        """Generate comprehensive client report."""
        report_data = {
            'client': self.client_name,
            'date': datetime.now().isoformat(),
            'jobs_completed': self.get_completed_jobs(),
            'production_time': self.get_production_time(),
            'quality_metrics': self.get_quality_metrics(),
            'resource_usage': self.get_resource_usage()
        }
        
        # Save and send report
        with open(f"reports/{self.client_name}_$(date +%Y%m%d).json", 'w') as f:
            json.dump(report_data, f, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 client_production.py <client_name>")
        sys.exit(1)
    
    production = ClientProduction(sys.argv[1])
    production.process_project()
```

### Intelligent Batch Scheduler
```python
#!/usr/bin/env python3
# batch_scheduler.py - Intelligent production scheduling

import subprocess
import json
from datetime import datetime, timedelta

class BatchScheduler:
    def __init__(self):
        self.load_production_constraints()
        self.analyze_pending_jobs()
    
    def load_production_constraints(self):
        """Load production constraints and resources."""
        self.constraints = {
            'max_daily_time': 8 * 60,  # 8 hours in minutes
            'max_pen_changes': 100,
            'available_pens': self.get_available_pens(),
            'paper_inventory': self.get_paper_inventory()
        }
    
    def optimize_production_schedule(self):
        """Create optimal production schedule."""
        jobs = self.get_pending_jobs()
        
        # Sort by optimization criteria
        jobs.sort(key=lambda x: (
            x.get('priority', 3),
            x.get('pen_changes', 0),
            x.get('estimated_time', 0)
        ))
        
        # Create schedule batches
        schedule = self.create_schedule_batches(jobs)
        
        # Execute optimized schedule
        self.execute_schedule(schedule)
    
    def create_schedule_batches(self, jobs):
        """Create optimized schedule batches."""
        batches = []
        current_batch = []
        current_time = 0
        current_pen_changes = 0
        
        for job in jobs:
            job_time = job.get('estimated_time', 0)
            job_pen_changes = job.get('pen_changes', 0)
            
            # Check if job fits in current batch
            if (current_time + job_time <= self.constraints['max_daily_time'] and
                current_pen_changes + job_pen_changes <= self.constraints['max_pen_changes']):
                
                current_batch.append(job)
                current_time += job_time
                current_pen_changes += job_pen_changes
            else:
                # Start new batch
                if current_batch:
                    batches.append(current_batch)
                current_batch = [job]
                current_time = job_time
                current_pen_changes = job_pen_changes
        
        # Add final batch
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def execute_schedule(self, schedule):
        """Execute optimized production schedule."""
        for i, batch in enumerate(schedule):
            print(f"🚀 Executing batch {i+1}/{len(schedule)}")
            
            # Plan batch with optimization
            job_names = [job['name'] for job in batch]
            subprocess.run([
                "vfab", "plan"
            ] + job_names + [
                "--optimize-batch",
                "--pen-order", self.calculate_optimal_pen_order(batch)
            ])
            
            # Execute batch
            subprocess.run([
                "vfab", "plot-all",
                "--monitor", "--batch-id", str(i+1)
            ])

if __name__ == "__main__":
    scheduler = BatchScheduler()
    scheduler.optimize_production_schedule()
```

---

## 🔧 Advanced Batch Configuration

### Production Templates
```bash
# Create production templates
vfab template create --name "client_standard" \
    --preset hq \
    --pen-mapping "2,1,3" \
    --quality-checks \
    --documentation

vfab template create --name "workshop_fast" \
    --preset fast \
    --pen-mapping "auto" \
    --minimal-documentation

# Apply templates
vfab plan-all --template client_standard
vfab add design.svg --template workshop_fast
```

### Resource Constraints
```bash
# Set production constraints
vfab config production \
    --max-daily-time 6h \
    --max-pen-changes 80 \
    --paper-budget 100 \
    --quality-threshold 95

# Plan with constraints
vfab plan-all --respect-constraints --optimize-within-limits
```

### Quality Gates
```bash
# Set quality gates for production
vfab config quality-gates \
    --min-success-rate 98 \
    --max-replot-rate 2 \
    --min-customer-satisfaction 4.5

# Production with quality enforcement
vfab plot-all --enforce-quality-gates --auto-hold-on-failure
```

---

## 📊 Production KPIs & Metrics

### Key Performance Indicators
```bash
# Daily KPI dashboard
vfab kpi dashboard --daily --show-trends

# Production efficiency metrics
vfab analyze efficiency --by-job-type --by-time-of-day

# Resource utilization KPIs
vfab kpi resources --utilization --cost-per-unit --waste-analysis
```

### Benchmarking
```bash
# Production benchmarking
vfab benchmark production --period last_30_days --industry-comparison

# Performance improvement tracking
vfab analyze improvements --since "2025-10-01" --by-metric

# Capacity planning
vfab analyze capacity --current --projected --growth-scenarios
```

---

## 💡 Batch Production Pro Tips

### Efficiency Optimization
- 🎯 **Group similar jobs** - Same paper size, pen requirements
- ⚡ **Optimize globally** - Consider entire batch, not individual jobs
- 📊 **Track metrics** - Use data to improve processes
- 🤖 **Automate repetitive tasks** - Scripts for routine operations

### Quality Assurance
- ✅ **Implement quality gates** - Automatic holds on quality drops
- 📋 **Standardize templates** - Consistent production parameters
- 📹 **Document everything** - Photos, videos, metrics
- 🔄 **Continuous improvement** - Use analytics to optimize

### Resource Management
- 🖊️ **Balance pen wear** - Distribute usage across pens
- 📄 **Optimize paper usage** - Minimize waste, track consumption
- ⏰ **Schedule maintenance** - Prevent downtime during production
- 💰 **Track costs** - Know your true production costs

---

## 🚨 Production Troubleshooting

### Batch Production Issues
```bash
# Batch planning problems
vfab diagnose batch-planning --show-conflicts --suggest-fixes

# Queue optimization issues
vfab diagnose queue-optimization --identify-bottlenecks

# Resource constraint conflicts
vfab diagnose resource-conflicts --suggest-alternatives
```

### Recovery Procedures
```bash
# Batch failure recovery
vfab recovery batch --batch-id 3 --resume-from-failure

# Partial batch completion
vfab recovery partial-batch --complete-remaining --preserve-completed

# Quality issue recovery
vfab recovery quality --replot-failed --adjust-parameters
```

---

**🎯 Goal:** Achieve maximum production efficiency with consistent quality and minimal waste.

**📚 Next:** [Studio Management](studio-management.md) for complete professional operations.