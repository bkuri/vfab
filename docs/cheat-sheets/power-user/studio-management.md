# Studio Management Cheat Sheet

## 🧭 Quick Navigation
- **Batch production workflows?** [Batch Production](batch-production.md)
- **Automate your studio?** [Automation Scripts](automation-scripts.md)
- **Optimize performance?** [Performance Tuning](performance-tuning.md)
- **Configuration help?** [Configuration Reference](../reference/configuration.md)

---

## **Studio Overview Dashboard**

### **Daily Status Check**
```bash
# Complete studio status
echo "=== vfab Studio Status ==="
echo "System Health:"
vfab system status
echo ""
echo "Current Queue:"
vfab list
echo ""
echo "Recent Statistics:"
vfab stats --days 7
echo ""
echo "Hardware Status:"
vfab check --hardware
```

### **Workspace Organization**
```bash
# Standard studio directory structure
mkdir -p studio/{active_jobs,completed,templates,materials,logs,backups}
cd studio

# Initialize vfab workspace
vfab init --workspace-type studio

# Set up project templates
mkdir templates/{business_cards,art_prints,logos,posters}
```

## **Job Management Systems**

### **Job Tracking Spreadsheet**
```python
# job_tracker.py
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class StudioJobTracker:
    def __init__(self, workspace="studio"):
        self.workspace = Path(workspace)
        self.jobs_file = self.workspace / "jobs.json"
        self.load_jobs()
    
    def load_jobs(self):
        if self.jobs_file.exists():
            with open(self.jobs_file) as f:
                self.jobs = json.load(f)
        else:
            self.jobs = {}
    
    def save_jobs(self):
        with open(self.jobs_file, 'w') as f:
            json.dump(self.jobs, f, indent=2, default=str)
    
    def add_job(self, job_id, client, description, priority='normal'):
        """Add new job to tracking system"""
        self.jobs[job_id] = {
            'client': client,
            'description': description,
            'priority': priority,
            'status': 'queued',
            'created': datetime.now().isoformat(),
            'started': None,
            'completed': None,
            'files': [],
            'notes': []
        }
        self.save_jobs()
        print(f"Added job {job_id} for {client}")
    
    def start_job(self, job_id):
        """Mark job as started"""
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = 'in_progress'
            self.jobs[job_id]['started'] = datetime.now().isoformat()
            self.save_jobs()
    
    def complete_job(self, job_id, notes=""):
        """Mark job as completed"""
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = 'completed'
            self.jobs[job_id]['completed'] = datetime.now().isoformat()
            if notes:
                self.jobs[job_id]['notes'].append({
                    'timestamp': datetime.now().isoformat(),
                    'note': notes
                })
            self.save_jobs()
    
    def get_active_jobs(self):
        """Get all active jobs"""
        return {k: v for k, v in self.jobs.items() 
                if v['status'] in ['queued', 'in_progress']}
    
    def generate_report(self, days=30):
        """Generate studio performance report"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_jobs = {k: v for k, v in self.jobs.items() 
                      if datetime.fromisoformat(v['created']) > cutoff_date}
        
        total_jobs = len(recent_jobs)
        completed_jobs = len([j for j in recent_jobs.values() if j['status'] == 'completed'])
        
        print(f"Studio Report - Last {days} days")
        print(f"Total Jobs: {total_jobs}")
        print(f"Completed: {completed_jobs}")
        print(f"Completion Rate: {completed_jobs/total_jobs*100:.1f}%")
        
        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'completion_rate': completed_jobs/total_jobs*100
        }

# Usage
if __name__ == "__main__":
    tracker = StudioJobTracker()
    
    # Add example jobs
    tracker.add_job("JOB001", "Acme Corp", "Business cards - 500 units", "high")
    tracker.add_job("JOB002", "Local Artist", "Art prints - 20 units", "normal")
    
    # Generate report
    tracker.generate_report()
```

### **Priority Queue Management**
```bash
#!/bin/bash
# priority_queue.sh

# Function to add job with priority
add_priority_job() {
    local file=$1
    local priority=$2  # high, normal, low
    local job_id=$3
    
    # Add priority tag to filename
    priority_file="${priority}_${job_id}_$(basename "$file")"
    
    # Copy to priority queue
    cp "$file" "studio/active_jobs/${priority_file}"
    
    # Add to vfab with priority
    case $priority in
        "high")
            vfab add --priority high "$file"
            ;;
        "normal")
            vfab add "$file"
            ;;
        "low")
            vfab add --priority low "$file"
            ;;
    esac
    
    echo "Added $job_id with $priority priority"
}

# Function to reorganize queue by priority
reorganize_queue() {
    echo "Reorganizing queue by priority..."
    
    # Get current queue
    vfab list > current_queue.txt
    
    # Extract high priority jobs
    grep "HIGH" current_queue.txt > high_priority.txt
    grep "NORMAL" current_queue.txt > normal_priority.txt
    grep "LOW" current_queue.txt > low_priority.txt
    
    # Clear and rebuild queue
    vfab remove --all
    
    # Add back in priority order
    while IFS= read -r line; do
        job_file=$(echo "$line" | awk '{print $NF}')
        vfab add --priority high "$job_file"
    done < high_priority.txt
    
    while IFS= read -r line; do
        job_file=$(echo "$line" | awk '{print $NF}')
        vfab add "$job_file"
    done < normal_priority.txt
    
    while IFS= read -r line; do
        job_file=$(echo "$line" | awk '{print $NF}')
        vfab add --priority low "$job_file"
    done < low_priority.txt
    
    echo "Queue reorganized by priority"
}
```

## **Resource Management**

### **Material Inventory System**
```python
# material_manager.py
import json
from datetime import datetime, timedelta
from pathlib import Path

class MaterialManager:
    def __init__(self):
        self.inventory_file = Path("studio/materials/inventory.json")
        self.load_inventory()
    
    def load_inventory(self):
        if self.inventory_file.exists():
            with open(self.inventory_file) as f:
                self.inventory = json.load(f)
        else:
            self.inventory = {
                'paper': {},
                'pens': {},
                'other': {}
            }
    
    def save_inventory(self):
        self.inventory_file.parent.mkdir(exist_ok=True)
        with open(self.inventory_file, 'w') as f:
            json.dump(self.inventory, f, indent=2, default=str)
    
    def add_paper(self, paper_type, size, quantity, supplier=""):
        """Add paper to inventory"""
        key = f"{paper_type}_{size}"
        if key not in self.inventory['paper']:
            self.inventory['paper'][key] = {
                'type': paper_type,
                'size': size,
                'quantity': 0,
                'supplier': supplier,
                'last_updated': None
            }
        
        self.inventory['paper'][key]['quantity'] += quantity
        self.inventory['paper'][key]['last_updated'] = datetime.now().isoformat()
        self.save_inventory()
    
    def use_paper(self, paper_type, size, quantity=1):
        """Remove paper from inventory"""
        key = f"{paper_type}_{size}"
        if key in self.inventory['paper']:
            self.inventory['paper'][key]['quantity'] -= quantity
            self.inventory['paper'][key]['last_updated'] = datetime.now().isoformat()
            self.save_inventory()
        else:
            print(f"Warning: {paper_type} {size} not found in inventory")
    
    def check_low_stock(self, threshold=10):
        """Check for low stock items"""
        low_stock = []
        
        for item_key, item_data in self.inventory['paper'].items():
            if item_data['quantity'] < threshold:
                low_stock.append(item_data)
        
        return low_stock
    
    def generate_shopping_list(self):
        """Generate shopping list for low stock items"""
        low_stock = self.check_low_stock()
        
        if low_stock:
            print("Shopping List - Low Stock Items:")
            for item in low_stock:
                print(f"- {item['type']} {item['size']}: {item['quantity']} left")
        else:
            print("All items well stocked")
        
        return low_stock

# Usage
if __name__ == "__main__":
    manager = MaterialManager()
    
    # Add initial inventory
    manager.add_paper("Premium", "A4", 50, "OfficeSupply Co")
    manager.add_paper("Standard", "A3", 25, "PaperMart")
    
    # Check stock levels
    manager.generate_shopping_list()
```

### **Pen Usage Tracking**
```bash
#!/bin/bash
# pen_tracker.sh

PEN_LOG="studio/materials/pen_usage.log"

# Function to log pen change
log_pen_change() {
    local pen_color=$1
    local pen_type=$2
    local reason=$3
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Changed to $pen_color $pen_type - $reason" >> "$PEN_LOG"
    echo "Pen change logged: $pen_color $pen_type"
}

# Function to check pen usage
check_pen_usage() {
    echo "=== Pen Usage Summary ==="
    if [ -f "$PEN_LOG" ]; then
        echo "Recent changes:"
        tail -10 "$PEN_LOG"
        
        echo ""
        echo "Usage by color:"
        grep -c "Black" "$PEN_LOG" 2>/dev/null || echo "Black: 0"
        grep -c "Red" "$PEN_LOG" 2>/dev/null || echo "Red: 0"
        grep -c "Blue" "$PEN_LOG" 2>/dev/null || echo "Blue: 0"
    else
        echo "No pen usage data found"
    fi
}

# Function to estimate pen life
estimate_pen_life() {
    local pen_color=$1
    
    if [ -f "$PEN_LOG" ]; then
        local changes=$(grep -c "$pen_color" "$PEN_LOG" 2>/dev/null || echo "0")
        echo "$pen_color pen changed $changes times"
        
        if [ "$changes" -gt 5 ]; then
            echo "Consider stocking up on $pen_color pens"
        fi
    fi
}
```

## **Client Management**

### **Project Templates**
```bash
#!/bin/bash
# create_project_template.sh

create_project_template() {
    local template_name=$1
    local template_dir="studio/templates/$template_name"
    
    mkdir -p "$template_dir"
    
    # Create template structure
    cat > "$template_dir/template_info.json" << EOF
{
    "name": "$template_name",
    "description": "Template for $template_name projects",
    "default_settings": {
        "paper_size": "A4",
        "pen_speed": 30,
        "pen_force": 40
    },
    "checklist": [
        "Verify client requirements",
        "Check material availability",
        "Test plot on sample",
        "Final production run"
    ]
}
EOF

    # Create standard README
    cat > "$template_dir/README.md" << EOF
# $template_name Template

## Standard Workflow
1. Review client requirements
2. Prepare design files
3. Test plot
4. Production
5. Quality check
6. Delivery

## Common Settings
- Paper: A4 Premium
- Pen: Black 0.7mm
- Speed: 30%
- Force: 40%

## Quality Checklist
- [ ] Lines are crisp
- [ ] No pen skips
- [ ] Proper alignment
- [ ] Client approved
EOF

    echo "Created template: $template_name"
}

# Create standard templates
create_project_template "business_cards"
create_project_template "art_prints"
create_project_template "logos"
create_project_template "posters"
```

### **Client Project Setup**
```bash
#!/bin/bash
# setup_client_project.sh

setup_client_project() {
    local client_name=$1
    local project_type=$2
    local project_id=$3
    
    local project_dir="studio/active_jobs/${project_id}_${client_name}"
    mkdir -p "$project_dir"
    
    # Copy template
    if [ -d "studio/templates/$project_type" ]; then
        cp -r "studio/templates/$project_type/"* "$project_dir/"
    fi
    
    # Create project-specific files
    cat > "$project_dir/project_info.json" << EOF
{
    "project_id": "$project_id",
    "client": "$client_name",
    "type": "$project_type",
    "created": "$(date -Iseconds)",
    "status": "setup",
    "files": [],
    "notes": []
}
EOF

    # Create working directories
    mkdir -p "$project_dir"/{designs,plots,final,logs}
    
    echo "Project setup complete: $project_dir"
}

# Usage example
# setup_client_project "Acme_Corp" "business_cards" "JOB001"
```

## **Maintenance Scheduling**

### **Automated Maintenance Script**
```bash
#!/bin/bash
# studio_maintenance.sh

STUDIO_DIR="studio"
LOG_FILE="$STUDIO_DIR/logs/maintenance.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Daily maintenance
daily_maintenance() {
    log_message "Starting daily maintenance"
    
    # Backup job data
    cp "$STUDIO_DIR/jobs.json" "$STUDIO_DIR/backups/jobs_$(date +%Y%m%d).json"
    
    # Clean old logs (keep 30 days)
    find "$STUDIO_DIR/logs" -name "*.log" -mtime +30 -delete
    
    # Check system health
    vfab system status >> "$STUDIO_DIR/logs/daily_health_$(date +%Y%m%d).txt"
    
    # Generate daily report
    vfab stats --days 1 >> "$STUDIO_DIR/logs/daily_stats_$(date +%Y%m%d).txt"
    
    log_message "Daily maintenance completed"
}

# Weekly maintenance
weekly_maintenance() {
    log_message "Starting weekly maintenance"
    
    # Check material inventory
    python material_manager.py --check-stock >> "$STUDIO_DIR/logs/weekly_inventory_$(date +%Y%m%d).txt"
    
    # Clean completed jobs older than 90 days
    find "$STUDIO_DIR/completed" -type d -mtime +90 -exec rm -rf {} \;
    
    # Update software
    echo "Checking for updates..." >> "$STUDIO_DIR/logs/weekly_update_$(date +%Y%m%d).txt"
    
    log_message "Weekly maintenance completed"
}

# Monthly maintenance
monthly_maintenance() {
    log_message "Starting monthly maintenance"
    
    # Deep clean workspace
    find "$STUDIO_DIR" -name "*.tmp" -delete
    find "$STUDIO_DIR" -name "*.cache" -delete
    
    # Archive old projects
    find "$STUDIO_DIR/completed" -type d -mtime +365 -exec tar -czf "archive/{}.tar.gz" {} \; -exec rm -rf {} \;
    
    # Generate monthly report
    python job_tracker.py --report --days 30 >> "$STUDIO_DIR/logs/monthly_report_$(date +%Y%m%d).txt"
    
    log_message "Monthly maintenance completed"
}

# Check what type of maintenance to run
case $1 in
    "daily")
        daily_maintenance
        ;;
    "weekly")
        weekly_maintenance
        ;;
    "monthly")
        monthly_maintenance
        ;;
    *)
        echo "Usage: $0 {daily|weekly|monthly}"
        exit 1
        ;;
esac
```

## **Performance Monitoring**

### **Studio Dashboard**
```python
# studio_dashboard.py
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class StudioDashboard:
    def __init__(self):
        self.studio_dir = Path("studio")
        self.load_data()
    
    def load_data(self):
        # Load jobs
        jobs_file = self.studio_dir / "jobs.json"
        if jobs_file.exists():
            with open(jobs_file) as f:
                self.jobs = json.load(f)
        else:
            self.jobs = {}
        
        # Load inventory
        inventory_file = self.studio_dir / "materials/inventory.json"
        if inventory_file.exists():
            with open(inventory_file) as f:
                self.inventory = json.load(f)
        else:
            self.inventory = {}
    
    def get_current_status(self):
        """Get current studio status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'active_jobs': len([j for j in self.jobs.values() if j['status'] in ['queued', 'in_progress']]),
            'completed_today': 0,
            'queue_length': 0,
            'low_stock_items': 0
        }
        
        # Get vfab queue length
        try:
            result = subprocess.run(['vfab', 'list'], capture_output=True, text=True)
            status['queue_length'] = len(result.stdout.strip().split('\n')) - 1
        except:
            status['queue_length'] = 0
        
        # Count completed jobs today
        today = datetime.now().date()
        for job in self.jobs.values():
            if job['status'] == 'completed' and 'completed' in job:
                completed_date = datetime.fromisoformat(job['completed']).date()
                if completed_date == today:
                    status['completed_today'] += 1
        
        return status
    
    def display_dashboard(self):
        """Display formatted dashboard"""
        status = self.get_current_status()
        
        print("=== vfab Studio Dashboard ===")
        print(f"Updated: {status['timestamp']}")
        print("")
        print("📊 Job Status:")
        print(f"  Active Jobs: {status['active_jobs']}")
        print(f"  Completed Today: {status['completed_today']}")
        print(f"  Queue Length: {status['queue_length']}")
        print("")
        
        # System health
        print("🔧 System Health:")
        try:
            result = subprocess.run(['vfab', 'system', 'status'], capture_output=True, text=True)
            print(f"  {result.stdout.strip()}")
        except:
            print("  Unable to get system status")
        print("")
        
        # Recent activity
        print("📝 Recent Activity:")
        recent_jobs = sorted(self.jobs.values(), 
                           key=lambda x: x.get('created', ''), 
                           reverse=True)[:3]
        for job in recent_jobs:
            print(f"  {job.get('client', 'Unknown')}: {job.get('description', 'No description')}")
        
        print("")
        print("Use 'vfab list' for full queue details")

# Usage
if __name__ == "__main__":
    dashboard = StudioDashboard()
    dashboard.display_dashboard()
```

## **Related Cheat Sheets**
- [Batch Production](batch-production.md) - High-volume production workflows
- [Performance Tuning](performance-tuning.md) - Optimize studio performance
- [Automation Scripts](automation-scripts.md) - Advanced studio automation

## **Studio Management Tips**
- **Consistent organization**: Use standard directory structures
- **Track everything**: Jobs, materials, time, and client information
- **Regular maintenance**: Daily, weekly, and monthly tasks
- **Monitor performance**: Use dashboards and reports
- **Backup regularly**: Protect your business data