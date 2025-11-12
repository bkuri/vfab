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
    plotty add "$file" --name "Client: $basename" --paper a4
done

# Import with metadata
for file in designs/approved/*.svg; do
    basename=$(basename "$file" .svg)
    plotty add "$file" \
        --name "Client: $basename" \
        --paper a4 \
        --priority normal \
        --tags "client,approved,$(date +%Y-%m)"
done
```

### Smart Batch Categorization
```bash
# Categorize by type
plotty add logos/*.svg --name "Client: Logo" --category "logo"
plotty add cards/*.svg --name "Client: Business Card" --category "card"
plotty add letterhead/*.svg --name "Client: Letterhead" --category "letterhead"

# Batch by priority
plotty add urgent/*.svg --priority high
plotty add normal/*.svg --priority normal
plotty add backlog/*.svg --priority low
```

---

## ⚡ Intelligent Batch Planning

### Global Optimization Strategies
```bash
# Plan all jobs with global pen optimization
plotty plan-all --preset fast --optimize-pens --global-pen-order

# Plan by priority
plotty plan-all --priority-order --optimize-pens

# Plan by time constraints
plotty plan-all --max-time-per-job 30m --preset fast
```

### Advanced Planning Options
```bash
# Plan with custom pen order
plotty plan-all --pen-order 2,1,3,4 --minimize-distance

# Plan with quality tiers
plotty plan-all --quality-tiers --auto-preset-selection

# Plan with resource constraints
plotty plan-all --max-pen-changes 50 --max-total-time 4h
```

### Selective Batch Planning
```bash
# Plan specific job categories
plotty plan "Client: Logo*" --preset hq
plotty plan "Client: Business Card*" --preset fast

# Plan by date range
plotty plan --added-after "2025-11-01" --added-before "2025-11-07"

# Plan by complexity
plotty plan-all --complexity-low --preset fast
plotty plan-all --complexity-high --preset hq
```

### Planning Analysis
```bash
# Compare planning strategies
plotty plan-all --preset fast --dry-run --save-as fast_plan
plotty plan-all --preset hq --dry-run --save-as hq_plan
plotty compare fast_plan hq_plan --show-time-estimates

# Analyze planning efficiency
plotty analyze planning --show-bottlenecks --suggest-improvements
```

---

## 🚀 Automated Batch Plotting

### Standard Batch Execution
```bash
# Plot all planned jobs
plotty plot-all

# Plot with safety monitoring
plotty plot-all --preset safe --monitor --auto-retry

# Plot with progress notifications
plotty plot-all --notify-on-complete --notify-on-error
```

### Advanced Batch Plotting
```bash
# Plot with time constraints
plotty plot-all --max-total-time 6h --auto-pause

# Plot with resource management
plotty plot-all --pen-usage-tracking --paper-usage-tracking

# Plot with quality control
plotty plot-all --quality-checks --auto-replot-failed
```

### Conditional Batch Plotting
```bash
# Plot only jobs under time threshold
plotty plot-all --max-job-time 20m

# Plot high-priority jobs first
plotty plot-all --priority-order --skip-low-priority

# Plot with automatic error recovery
plotty plot-all --auto-recovery --max-retries 2
```

### Parallel Processing (Multiple Devices)
```bash
# Distribute across multiple devices
plotty plot-all --devices axidraw_v3_1,axidraw_v3_2 --load-balance

# Device-specific optimization
plotty plot-all --device-1-preset fast --device-2-preset hq

# Monitor multiple devices
plotty monitor --all-devices --consolidated-status
```

---

## 📊 Queue Management & Monitoring

### Real-time Queue Monitoring
```bash
# Live queue monitoring
plotty list queue --watch --refresh 30s

# Detailed queue analysis
plotty list queue --detailed --show-estimates --show-pen-changes

# Queue performance metrics
plotty analyze queue --efficiency --bottlenecks --optimization-suggestions
```

### Intelligent Queue Organization
```bash
# Group jobs by client
plotty queue group --by-client "Acme Corp"

# Reorder by optimization
plotty queue reorder --by-pen-efficiency

# Split large batches
plotty queue split --batch-size 10 --name-suffix "batch_{n}"
```

### Automated Queue Management
```bash
# Smart queue cleanup
plotty queue cleanup --completed --older-than 1d --archive

# Queue optimization
plotty queue optimize --global-pen-order --minimize-total-time

# Queue backup and restore
plotty queue backup --file "queue_backup_$(date +%Y%m%d).json"
plotty queue restore --file "queue_backup_20251107.json"
```

---

## 📈 Production Analytics & Reporting

### Comprehensive Production Reports
```bash
# Daily production summary
plotty report production --date today \
    --include-time-analysis \
    --include-resource-usage \
    --export "production_report_$(date +%Y%m%d).pdf"

# Client-specific reports
plotty report client --name "Acme Corp" \
    --date-range "2025-11-01:2025-11-07" \
    --include-cost-analysis \
    --include-quality-metrics

# Batch performance analysis
plotty analyze batch --name "November Production" \
    --show-efficiency-trends \
    --identify-improvements
```

### Resource Utilization Tracking
```bash
# Pen usage analysis
plotty analyze pens --usage-patterns --wear-analysis --replacement-schedule

# Paper consumption tracking
plotty analyze paper --consumption-by-job --cost-analysis --waste-reduction

# Device performance metrics
plotty analyze devices --uptime --error-rates --maintenance-schedule
```

### Quality Metrics
```bash
# Quality trend analysis
plotty analyze quality --trends --by-pen --by-paper --by-complexity

# Error rate analysis
plotty analyze errors --by-job-type --by-device --by-time-of-day

# Customer satisfaction tracking
plotty analyze satisfaction --by-client --by-job-type --correlate-quality
```

---

## 🤖 Production Automation Scripts

### Daily Production Routine
```bash
#!/bin/bash
# daily_production.sh - Automated daily production

echo "🌅 Starting daily production routine..."

# Morning system check
plotty check ready --detailed
if [ $? -ne 0 ]; then
    echo "❌ System check failed. Aborting production."
    exit 1
fi

# Load today's production schedule
plotty load schedule --file "today/production_schedule.json"

# Optimize for today's constraints
plotty plan-all --optimize-for-today --resource-constraints

# Start production with monitoring
plotty plot-all --monitor --notify-on-complete --auto-recovery

# Generate end-of-day report
plotty report daily --auto-generate --email-studio

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
                "plotty", "add", design['file'],
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
            "plotty", "plan-all",
            "--pen-mapping", pen_mapping,
            "--preset", quality_preset,
            "--client-standards", self.client_name
        ])
    
    def execute_production(self):
        """Execute production with client monitoring."""
        subprocess.run([
            "plotty", "plot-all",
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
                "plotty", "plan"
            ] + job_names + [
                "--optimize-batch",
                "--pen-order", self.calculate_optimal_pen_order(batch)
            ])
            
            # Execute batch
            subprocess.run([
                "plotty", "plot-all",
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
plotty template create --name "client_standard" \
    --preset hq \
    --pen-mapping "2,1,3" \
    --quality-checks \
    --documentation

plotty template create --name "workshop_fast" \
    --preset fast \
    --pen-mapping "auto" \
    --minimal-documentation

# Apply templates
plotty plan-all --template client_standard
plotty add design.svg --template workshop_fast
```

### Resource Constraints
```bash
# Set production constraints
plotty config production \
    --max-daily-time 6h \
    --max-pen-changes 80 \
    --paper-budget 100 \
    --quality-threshold 95

# Plan with constraints
plotty plan-all --respect-constraints --optimize-within-limits
```

### Quality Gates
```bash
# Set quality gates for production
plotty config quality-gates \
    --min-success-rate 98 \
    --max-replot-rate 2 \
    --min-customer-satisfaction 4.5

# Production with quality enforcement
plotty plot-all --enforce-quality-gates --auto-hold-on-failure
```

---

## 📊 Production KPIs & Metrics

### Key Performance Indicators
```bash
# Daily KPI dashboard
plotty kpi dashboard --daily --show-trends

# Production efficiency metrics
plotty analyze efficiency --by-job-type --by-time-of-day

# Resource utilization KPIs
plotty kpi resources --utilization --cost-per-unit --waste-analysis
```

### Benchmarking
```bash
# Production benchmarking
plotty benchmark production --period last_30_days --industry-comparison

# Performance improvement tracking
plotty analyze improvements --since "2025-10-01" --by-metric

# Capacity planning
plotty analyze capacity --current --projected --growth-scenarios
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
plotty diagnose batch-planning --show-conflicts --suggest-fixes

# Queue optimization issues
plotty diagnose queue-optimization --identify-bottlenecks

# Resource constraint conflicts
plotty diagnose resource-conflicts --suggest-alternatives
```

### Recovery Procedures
```bash
# Batch failure recovery
plotty recovery batch --batch-id 3 --resume-from-failure

# Partial batch completion
plotty recovery partial-batch --complete-remaining --preserve-completed

# Quality issue recovery
plotty recovery quality --replot-failed --adjust-parameters
```

---

**🎯 Goal:** Achieve maximum production efficiency with consistent quality and minimal waste.

**📚 Next:** [Studio Management](studio-management.md) for complete professional operations.