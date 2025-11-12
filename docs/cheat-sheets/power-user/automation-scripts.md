# Automation Scripts Cheat Sheet

## **Workflow Automation**

### **Automated Job Processing**
```python
# auto_job_processor.py
import os
import time
import json
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class JobProcessor(FileSystemEventHandler):
    def __init__(self, input_dir, output_dir, config_file="config.json"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.config = self.load_config(config_file)
        self.processing = set()
        
        # Ensure directories exist
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
    def load_config(self, config_file):
        """Load automation configuration"""
        default_config = {
            "auto_optimize": True,
            "quality_check": True,
            "backup_originals": True,
            "notification_email": "",
            "processing_delay": 5,  # seconds
            "max_queue_size": 50
        }
        
        if Path(config_file).exists():
            with open(config_file) as f:
                user_config = json.load(f)
            default_config.update(user_config)
        
        return default_config
    
    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix.lower() != '.svg':
            return
            
        # Avoid processing the same file multiple times
        if str(file_path) in self.processing:
            return
            
        self.processing.add(str(file_path))
        
        print(f"New file detected: {file_path.name}")
        
        # Wait for file to be fully written
        time.sleep(self.config['processing_delay'])
        
        try:
            self.process_file(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        finally:
            self.processing.discard(str(file_path))
    
    def process_file(self, file_path):
        """Process a single SVG file"""
        print(f"Processing {file_path.name}...")
        
        # Step 1: Backup original if enabled
        if self.config['backup_originals']:
            backup_path = self.output_dir / "backups" / file_path.name
            backup_path.parent.mkdir(exist_ok=True)
            backup_path.write_bytes(file_path.read_bytes())
        
        # Step 2: Optimize if enabled
        processed_file = file_path
        if self.config['auto_optimize']:
            processed_file = self.optimize_file(file_path)
        
        # Step 3: Quality check if enabled
        if self.config['quality_check']:
            if not self.quality_check(processed_file):
                print(f"Quality check failed for {file_path.name}")
                return False
        
        # Step 4: Add to ploTTY queue
        self.add_to_queue(processed_file)
        
        # Step 5: Log processing
        self.log_processing(file_path, processed_file)
        
        print(f"Successfully processed {file_path.name}")
        return True
    
    def optimize_file(self, file_path):
        """Optimize SVG file for faster plotting"""
        output_path = self.output_dir / "optimized" / f"opt_{file_path.name}"
        output_path.parent.mkdir(exist_ok=True)
        
        # Use vpype for optimization
        cmd = [
            'vpype', 'read', str(file_path),
            'linemerge', '--tolerance', '0.3mm',
            'linesort',
            'simplify', '--tolerance', '0.2mm',
            'write', str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Optimized {file_path.name}")
            return output_path
        else:
            print(f"Optimization failed for {file_path.name}: {result.stderr}")
            return file_path
    
    def quality_check(self, file_path):
        """Perform quality check on processed file"""
        try:
            # Use ploTTY to check file
            result = subprocess.run(['plotty', 'check', str(file_path)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Quality check passed for {file_path.name}")
                return True
            else:
                print(f"Quality check failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Quality check error: {e}")
            return False
    
    def add_to_queue(self, file_path):
        """Add file to ploTTY queue with space management"""
        # Check queue size
        result = subprocess.run(['plotty', 'list'], capture_output=True, text=True)
        queue_size = len(result.stdout.strip().split('\n')) - 1
        
        if queue_size >= self.config['max_queue_size']:
            print(f"Queue full ({queue_size} jobs), skipping {file_path.name}")
            return False
        
        # Add to queue
        result = subprocess.run(['plotty', 'add', str(file_path)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Added {file_path.name} to queue")
            return True
        else:
            print(f"Failed to add {file_path.name} to queue: {result.stderr}")
            return False
    
    def log_processing(self, original_file, processed_file):
        """Log processing details"""
        log_entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'original_file': str(original_file),
            'processed_file': str(processed_file),
            'status': 'success'
        }
        
        log_file = self.output_dir / "processing_log.json"
        logs = []
        
        if log_file.exists():
            with open(log_file) as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def start_monitoring(self):
        """Start monitoring the input directory"""
        observer = Observer()
        observer.schedule(self, str(self.input_dir), recursive=False)
        observer.start()
        
        print(f"Monitoring {self.input_dir} for new SVG files...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        
        observer.join()

# Usage
if __name__ == "__main__":
    processor = JobProcessor("input", "output")
    processor.start_monitoring()
```

### **Scheduled Automation**
```python
# scheduled_tasks.py
import schedule
import time
import subprocess
from datetime import datetime

class ScheduledAutomation:
    def __init__(self):
        self.setup_schedule()
    
    def setup_schedule(self):
        """Setup scheduled tasks"""
        
        # Daily tasks
        schedule.every().day.at("09:00").do(self.morning_routine)
        schedule.every().day.at("17:00").do(self.evening_routine)
        
        # Hourly tasks
        schedule.every().hour.do(self.hourly_maintenance)
        
        # Weekly tasks
        schedule.every().sunday.at("02:00").do(self.weekly_maintenance)
        
        # Custom intervals
        schedule.every(30).minutes.do(self.check_queue_status)
        schedule.every(10).minutes.do(self.monitor_system_health)
    
    def morning_routine(self):
        """Daily morning routine"""
        print(f"[{datetime.now()}] Running morning routine...")
        
        # System health check
        self.system_health_check()
        
        # Clear old temporary files
        self.cleanup_temp_files()
        
        # Check material inventory
        self.check_inventory()
        
        # Generate daily report
        self.generate_daily_report()
        
        print("Morning routine complete")
    
    def evening_routine(self):
        """Daily evening routine"""
        print(f"[{datetime.now()}] Running evening routine...")
        
        # Backup today's work
        self.backup_daily_work()
        
        # Process any remaining jobs
        self.process_remaining_jobs()
        
        # Generate evening report
        self.generate_evening_report()
        
        print("Evening routine complete")
    
    def hourly_maintenance(self):
        """Hourly maintenance tasks"""
        # Check ploTTY service status
        try:
            result = subprocess.run(['systemctl', 'is-active', 'plottyd'], 
                                  capture_output=True, text=True)
            if result.stdout.strip() != 'active':
                print(f"ploTTY service is not active: {result.stdout.strip()}")
                subprocess.run(['systemctl', 'restart', 'plottyd'])
        except Exception as e:
            print(f"Error checking ploTTY service: {e}")
        
        # Monitor memory usage
        self.check_memory_usage()
    
    def weekly_maintenance(self):
        """Weekly maintenance tasks"""
        print(f"[{datetime.now()}] Running weekly maintenance...")
        
        # Deep system cleanup
        self.deep_cleanup()
        
        # Database optimization
        self.optimize_database()
        
        # Update software
        self.update_software()
        
        # Generate weekly report
        self.generate_weekly_report()
        
        print("Weekly maintenance complete")
    
    def check_queue_status(self):
        """Check ploTTY queue status"""
        try:
            result = subprocess.run(['plotty', 'list'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            queue_size = len(lines) - 1 if lines else 0
            
            if queue_size > 40:
                print(f"Warning: Queue size is high ({queue_size} jobs)")
            elif queue_size == 0:
                print("Queue is empty")
            
        except Exception as e:
            print(f"Error checking queue status: {e}")
    
    def monitor_system_health(self):
        """Monitor system health metrics"""
        import psutil
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            print(f"Warning: High CPU usage ({cpu_percent}%)")
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            print(f"Warning: High memory usage ({memory.percent}%)")
        
        # Check disk space
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            print(f"Warning: Low disk space ({disk.percent}% used)")
    
    def system_health_check(self):
        """Comprehensive system health check"""
        print("Running system health check...")
        
        # ploTTY system status
        try:
            result = subprocess.run(['plotty', 'system', 'status'], 
                                  capture_output=True, text=True)
            print("ploTTY System Status:")
            print(result.stdout)
        except Exception as e:
            print(f"Error getting ploTTY status: {e}")
        
        # Hardware check
        try:
            result = subprocess.run(['plotty', 'check', '--hardware'], 
                                  capture_output=True, text=True)
            print("Hardware Status:")
            print(result.stdout)
        except Exception as e:
            print(f"Error checking hardware: {e}")
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        import glob
        
        temp_patterns = [
            '/tmp/plotty_*',
            '/var/tmp/plotty_*',
            '~/.cache/plotty/tmp/*'
        ]
        
        for pattern in temp_patterns:
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                    print(f"Removed temporary file: {file_path}")
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
    
    def check_inventory(self):
        """Check material inventory levels"""
        # This would integrate with your inventory system
        print("Checking material inventory...")
        # Implementation depends on your inventory tracking
    
    def generate_daily_report(self):
        """Generate daily performance report"""
        report_file = f"reports/daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(report_file, 'w') as f:
            f.write(f"Daily ploTTY Report - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("=" * 50 + "\n\n")
            
            # Queue status
            try:
                result = subprocess.run(['plotty', 'list'], capture_output=True, text=True)
                f.write("Queue Status:\n")
                f.write(result.stdout)
                f.write("\n")
            except:
                f.write("Unable to get queue status\n\n")
            
            # System statistics
            try:
                result = subprocess.run(['plotty', 'stats', '--days', '1'], 
                                      capture_output=True, text=True)
                f.write("Today's Statistics:\n")
                f.write(result.stdout)
                f.write("\n")
            except:
                f.write("Unable to get statistics\n\n")
        
        print(f"Daily report saved to {report_file}")
    
    def backup_daily_work(self):
        """Backup today's work"""
        import shutil
        
        backup_dir = f"backups/daily_backup_{datetime.now().strftime('%Y%m%d')}"
        
        # Backup ploTTY data
        if os.path.exists('/var/lib/plotty'):
            shutil.copytree('/var/lib/plotty', f"{backup_dir}/plotty_data", 
                          dirs_exist_ok=True)
        
        # Backup custom configurations
        if os.path.exists('config'):
            shutil.copytree('config', f"{backup_dir}/config", dirs_exist_ok=True)
        
        print(f"Daily backup completed: {backup_dir}")
    
    def process_remaining_jobs(self):
        """Process any remaining jobs in queue"""
        try:
            result = subprocess.run(['plotty', 'list'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            queue_size = len(lines) - 1 if lines else 0
            
            if queue_size > 0:
                print(f"Processing {queue_size} remaining jobs...")
                # You might want to extend working hours or notify someone
            else:
                print("No remaining jobs to process")
                
        except Exception as e:
            print(f"Error checking remaining jobs: {e}")
    
    def generate_evening_report(self):
        """Generate evening summary report"""
        # Similar to daily report but focused on completion status
        pass
    
    def deep_cleanup(self):
        """Perform deep system cleanup"""
        # Clean old logs
        import glob
        import time
        
        old_logs = glob.glob('logs/*.log')
        for log_file in old_logs:
            if time.time() - os.path.getmtime(log_file) > 30 * 24 * 3600:  # 30 days
                try:
                    os.remove(log_file)
                    print(f"Removed old log: {log_file}")
                except Exception as e:
                    print(f"Error removing {log_file}: {e}")
    
    def optimize_database(self):
        """Optimize ploTTY database"""
        try:
            result = subprocess.run(['plotty', 'db', 'optimize'], 
                                  capture_output=True, text=True)
            print("Database optimization:")
            print(result.stdout)
        except Exception as e:
            print(f"Database optimization error: {e}")
    
    def update_software(self):
        """Update ploTTY and dependencies"""
        print("Checking for software updates...")
        # Implementation depends on your package manager
        # For example: uv pip install --upgrade plotty
    
    def generate_weekly_report(self):
        """Generate comprehensive weekly report"""
        report_file = f"reports/weekly_report_{datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(report_file, 'w') as f:
            f.write(f"Weekly ploTTY Report - Week of {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Weekly statistics
            try:
                result = subprocess.run(['plotty', 'stats', '--days', '7'], 
                                      capture_output=True, text=True)
                f.write("Weekly Statistics:\n")
                f.write(result.stdout)
                f.write("\n")
            except:
                f.write("Unable to get weekly statistics\n\n")
        
        print(f"Weekly report saved to {report_file}")
    
    def check_memory_usage(self):
        """Check for memory issues"""
        import psutil
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            if proc.info['name'] == 'plottyd':
                memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                if memory_mb > 1000:  # More than 1GB
                    print(f"Warning: ploTTY using {memory_mb:.1f}MB memory")
    
    def run(self):
        """Run the scheduled task manager"""
        print("Scheduled automation started...")
        print("Press Ctrl+C to stop")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Usage
if __name__ == "__main__":
    automation = ScheduledAutomation()
    automation.run()
```

## **Integration Automation**

### **Webhook Integration**
```python
# webhook_automation.py
from flask import Flask, request, jsonify
import subprocess
import json
import tempfile
import os
from pathlib import Path

app = Flask(__name__)

class WebhookAutomation:
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="plotty_webhook_"))
        self.setup_routes()
    
    def setup_routes(self):
        """Setup webhook endpoints"""
        
        @app.route('/webhook/github', methods=['POST'])
        def github_webhook():
            """Handle GitHub webhook for design updates"""
            data = request.json
            
            # Verify it's a push to main branch
            if data.get('ref') == 'refs/heads/main':
                return self.handle_github_push(data)
            else:
                return jsonify({'status': 'ignored', 'reason': 'not main branch'})
        
        @app.route('/webhook/dropbox', methods=['POST'])
        def dropbox_webhook():
            """Handle Dropbox file updates"""
            data = request.json
            return self.handle_dropbox_update(data)
        
        @app.route('/api/add_job', methods=['POST'])
        def add_job_api():
            """REST API to add job"""
            data = request.json
            return self.add_job_via_api(data)
        
        @app.route('/api/status', methods=['GET'])
        def status_api():
            """Get ploTTY status"""
            return self.get_status()
    
    def handle_github_push(self, data):
        """Handle GitHub push webhook"""
        try:
            repo_url = data['repository']['clone_url']
            commit = data['after']
            
            # Clone repository
            repo_dir = self.temp_dir / f"repo_{commit[:8]}"
            subprocess.run(['git', 'clone', repo_url, str(repo_dir)], check=True)
            
            # Find SVG files
            svg_files = list(repo_dir.rglob("*.svg"))
            
            processed = []
            for svg_file in svg_files:
                if self.add_file_to_queue(svg_file):
                    processed.append(str(svg_file.name))
            
            return jsonify({
                'status': 'success',
                'commit': commit,
                'processed_files': processed
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    def handle_dropbox_update(self, data):
        """Handle Dropbox file update webhook"""
        # Implementation depends on Dropbox API
        return jsonify({'status': 'not_implemented'})
    
    def add_job_via_api(self, data):
        """Add job via REST API"""
        try:
            # Validate required fields
            if 'file_url' not in data:
                return jsonify({'error': 'file_url required'}), 400
            
            # Download file
            import requests
            response = requests.get(data['file_url'])
            response.raise_for_status()
            
            # Save to temporary file
            temp_file = self.temp_dir / f"api_job_{int(time.time())}.svg"
            temp_file.write_bytes(response.content)
            
            # Add to ploTTY queue
            if self.add_file_to_queue(temp_file, priority=data.get('priority', 'normal')):
                return jsonify({
                    'status': 'success',
                    'job_id': temp_file.stem,
                    'queue_position': self.get_queue_position()
                })
            else:
                return jsonify({'error': 'Failed to add to queue'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def get_status(self):
        """Get current ploTTY status"""
        try:
            # Get queue status
            result = subprocess.run(['plotty', 'list'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            queue_size = len(lines) - 1 if lines else 0
            
            # Get system status
            system_result = subprocess.run(['plotty', 'system', 'status'], 
                                         capture_output=True, text=True)
            
            return jsonify({
                'queue_size': queue_size,
                'system_status': system_result.stdout,
                'timestamp': time.time()
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def add_file_to_queue(self, file_path, priority='normal'):
        """Add file to ploTTY queue"""
        try:
            if priority == 'high':
                cmd = ['plotty', 'add', '--priority', 'high', str(file_path)]
            elif priority == 'low':
                cmd = ['plotty', 'add', '--priority', 'low', str(file_path)]
            else:
                cmd = ['plotty', 'add', str(file_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception:
            return False
    
    def get_queue_position(self):
        """Get current queue position"""
        try:
            result = subprocess.run(['plotty', 'list'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            return len(lines) - 1 if lines else 0
        except:
            return 0

# Usage
if __name__ == "__main__":
    webhook = WebhookAutomation()
    app.run(host='0.0.0.0', port=8080, debug=True)
```

### **Email Notifications**
```python
# email_notifications.py
import smtplib
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

class EmailNotifier:
    def __init__(self, config_file="email_config.json"):
        self.config = self.load_config(config_file)
    
    def load_config(self, config_file):
        """Load email configuration"""
        default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "from_email": "",
            "to_emails": [],
            "notifications": {
                "job_completed": True,
                "queue_empty": True,
                "error_occurred": True,
                "daily_summary": False
            }
        }
        
        try:
            with open(config_file) as f:
                user_config = json.load(f)
            default_config.update(user_config)
        except FileNotFoundError:
            print(f"Config file {config_file} not found, using defaults")
        
        return default_config
    
    def send_email(self, subject, body):
        """Send email notification"""
        if not self.config['username'] or not self.config['password']:
            print("Email credentials not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['from_email']
            msg['To'] = ', '.join(self.config['to_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['username'], self.config['password'])
            
            text = msg.as_string()
            server.sendmail(self.config['from_email'], self.config['to_emails'], text)
            server.quit()
            
            print(f"Email sent: {subject}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def notify_job_completed(self, job_name):
        """Notify when a job is completed"""
        if not self.config['notifications']['job_completed']:
            return
        
        subject = f"ploTTY Job Completed: {job_name}"
        body = f"""
Job completed successfully!

Job Name: {job_name}
Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Check ploTTY for more details.
        """
        
        self.send_email(subject, body)
    
    def notify_queue_empty(self):
        """Notify when queue becomes empty"""
        if not self.config['notifications']['queue_empty']:
            return
        
        subject = "ploTTY Queue Empty"
        body = f"""
All jobs in the ploTTY queue have been completed.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Ready for new jobs!
        """
        
        self.send_email(subject, body)
    
    def notify_error(self, error_message):
        """Notify when an error occurs"""
        if not self.config['notifications']['error_occurred']:
            return
        
        subject = "ploTTY Error Occurred"
        body = f"""
An error has occurred in ploTTY:

Error: {error_message}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check the system.
        """
        
        self.send_email(subject, body)
    
    def send_daily_summary(self):
        """Send daily summary report"""
        if not self.config['notifications']['daily_summary']:
            return
        
        try:
            # Get today's statistics
            result = subprocess.run(['plotty', 'stats', '--days', '1'], 
                                  capture_output=True, text=True)
            
            # Get current queue status
            queue_result = subprocess.run(['plotty', 'list'], 
                                        capture_output=True, text=True)
            lines = queue_result.stdout.strip().split('\n')
            queue_size = len(lines) - 1 if lines else 0
            
            subject = f"ploTTY Daily Summary - {datetime.now().strftime('%Y-%m-%d')}"
            body = f"""
Daily ploTTY Summary for {datetime.now().strftime('%Y-%m-%d')}

Today's Statistics:
{result.stdout}

Current Queue Status: {queue_size} jobs pending

System is operating normally.
            """
            
            self.send_email(subject, body)
            
        except Exception as e:
            print(f"Error generating daily summary: {e}")

# Usage example
if __name__ == "__main__":
    notifier = EmailNotifier()
    
    # Test notifications
    notifier.notify_job_completed("test_job.svg")
    notifier.send_daily_summary()
```

## **Advanced Automation**

### **Machine Learning Optimization**
```python
# ml_optimizer.py
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import json
import pickle
from pathlib import Path

class PlottingOptimizer:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.training_data = []
        self.model_file = Path("models/plotting_optimizer.pkl")
        self.data_file = Path("models/training_data.json")
        
        # Load existing model if available
        if self.model_file.exists():
            self.load_model()
    
    def collect_training_data(self, svg_file, actual_time, quality_score):
        """Collect training data from completed jobs"""
        # Extract features from SVG file
        features = self.extract_features(svg_file)
        
        # Add actual results
        training_point = {
            'features': features,
            'actual_time': actual_time,
            'quality_score': quality_score,
            'timestamp': datetime.now().isoformat()
        }
        
        self.training_data.append(training_point)
        self.save_training_data()
    
    def extract_features(self, svg_file):
        """Extract features from SVG file"""
        features = {}
        
        with open(svg_file, 'r') as f:
            content = f.read()
        
        # Basic features
        features['path_count'] = content.count('<path')
        features['circle_count'] = content.count('<circle')
        features['rect_count'] = content.count('<rect')
        features['total_elements'] = (features['path_count'] + 
                                   features['circle_count'] + 
                                   features['rect_count'])
        
        # Complexity features
        features['file_size'] = Path(svg_file).stat().st_size
        features['avg_path_length'] = self.estimate_avg_path_length(content)
        
        # Geometric features
        features['bounding_box_area'] = self.estimate_bounding_area(content)
        features['path_density'] = features['total_elements'] / max(1, features['bounding_box_area'])
        
        return features
    
    def estimate_avg_path_length(self, svg_content):
        """Estimate average path length from SVG content"""
        # Simplified estimation
        import re
        
        paths = re.findall(r'd="([^"]*)"', svg_content)
        if not paths:
            return 0
        
        total_length = 0
        for path in paths:
            # Count command characters as rough length estimate
            total_length += len([c for c in path if c.isalpha()])
        
        return total_length / len(paths) if paths else 0
    
    def estimate_bounding_area(self, svg_content):
        """Estimate bounding box area from SVG content"""
        # Look for viewBox or width/height attributes
        import re
        
        viewBox = re.search(r'viewBox="([^"]*)"', svg_content)
        if viewBox:
            values = list(map(float, viewBox.group(1).split()))
            return abs(values[2] - values[0]) * abs(values[3] - values[1])
        
        # Fallback to standard A4 size
        return 210 * 297  # A4 size in mm
    
    def train_model(self):
        """Train the optimization model"""
        if len(self.training_data) < 10:
            print("Need at least 10 training examples")
            return False
        
        # Prepare training data
        X = []
        y_time = []
        y_quality = []
        
        for data_point in self.training_data:
            features = list(data_point['features'].values())
            X.append(features)
            y_time.append(data_point['actual_time'])
            y_quality.append(data_point['quality_score'])
        
        X = np.array(X)
        y_time = np.array(y_time)
        y_quality = np.array(y_quality)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train models
        self.time_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.quality_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        self.time_model.fit(X_scaled, y_time)
        self.quality_model.fit(X_scaled, y_quality)
        
        # Save model
        self.save_model()
        
        print("Model trained successfully")
        return True
    
    def predict_optimal_settings(self, svg_file):
        """Predict optimal plotting settings for a new file"""
        if self.model is None:
            return self.get_default_settings()
        
        features = self.extract_features(svg_file)
        feature_vector = np.array(list(features.values())).reshape(1, -1)
        feature_scaled = self.scaler.transform(feature_vector)
        
        # Predict time and quality
        predicted_time = self.time_model.predict(feature_scaled)[0]
        predicted_quality = self.quality_model.predict(feature_scaled)[0]
        
        # Generate optimal settings based on predictions
        settings = self.optimize_settings_for_prediction(predicted_time, predicted_quality)
        
        return settings
    
    def optimize_settings_for_prediction(self, predicted_time, predicted_quality):
        """Generate optimal settings based on ML predictions"""
        settings = {}
        
        # Adjust speed based on predicted time
        if predicted_time > 300:  # More than 5 minutes
            settings['speed'] = 60  # High speed for long jobs
            settings['precision'] = 'low'
        elif predicted_time > 120:  # 2-5 minutes
            settings['speed'] = 45  # Medium speed
            settings['precision'] = 'medium'
        else:  # Less than 2 minutes
            settings['speed'] = 30  # Lower speed for quality
            settings['precision'] = 'high'
        
        # Adjust other settings based on quality prediction
        if predicted_quality < 0.7:
            settings['force'] = 50  # Higher force for better quality
            settings['smoothing'] = 'maximum'
        else:
            settings['force'] = 40
            settings['smoothing'] = 'standard'
        
        return settings
    
    def get_default_settings(self):
        """Get default settings when no model is available"""
        return {
            'speed': 40,
            'precision': 'medium',
            'force': 45,
            'smoothing': 'standard'
        }
    
    def save_model(self):
        """Save trained model"""
        self.model_file.parent.mkdir(exist_ok=True)
        
        model_data = {
            'time_model': self.time_model,
            'quality_model': self.quality_model,
            'scaler': self.scaler
        }
        
        with open(self.model_file, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self):
        """Load trained model"""
        try:
            with open(self.model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            self.time_model = model_data['time_model']
            self.quality_model = model_data['quality_model']
            self.scaler = model_data['scaler']
            self.model = True  # Mark as loaded
            
            print("Model loaded successfully")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def save_training_data(self):
        """Save training data"""
        self.data_file.parent.mkdir(exist_ok=True)
        
        with open(self.data_file, 'w') as f:
            json.dump(self.training_data, f, indent=2)

# Usage
if __name__ == "__main__":
    optimizer = PlottingOptimizer()
    
    # Example: Collect data from completed job
    # optimizer.collect_training_data("job1.svg", actual_time=180, quality_score=0.85)
    
    # Train model when enough data is collected
    # optimizer.train_model()
    
    # Predict optimal settings for new job
    # settings = optimizer.predict_optimal_settings("new_job.svg")
    # print(f"Optimal settings: {settings}")
```

## **Related Cheat Sheets**
- [Studio Management](studio-management.md) - Business automation workflows
- [Performance Tuning](performance-tuning.md) - System optimization
- [Batch Production](batch-production.md) - High-volume automation

## **Automation Tips**
- **Start small**: Begin with simple file monitoring and scale up
- **Error handling**: Always include robust error handling and logging
- **Testing**: Test automation scripts thoroughly before production use
- **Monitoring**: Monitor automated processes to ensure they're working correctly
- **Documentation**: Document your automation workflows for maintenance