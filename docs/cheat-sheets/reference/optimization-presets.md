# Optimization Presets Cheat Sheet

## **Quick Preset Selection**

### **Choose by Use Case**
```bash
# Fast drafting
vfab add --preset draft design.svg

# High quality final output
vfab add --preset quality final_art.svg

# Balanced performance
vfab add --preset balanced standard_job.svg

# delicate materials
vfab add --preset delicate fragile_design.svg

# Heavy materials
vfab add --preset heavy thick_cardstock.svg
```

## **Built-in Presets**

### **Speed-Based Presets**

#### **Draft Mode** - Maximum Speed
```yaml
# presets/draft.yaml
name: "Draft"
description: "Maximum speed for quick previews and testing"

plotting:
  motion:
    speed: 85                    # Very high speed
    acceleration: 2.5            # High acceleration
    pen_up_height: 80           # Fast pen lifts
    pen_down_force: 25           # Light pressure
    
  quality:
    precision: "low"            # Low precision for speed
    smoothing: false            # No smoothing
    corner_handling: "sharp"    # Sharp corners for speed
    
  hardware:
    skip_pen_lifts: true        # Skip unnecessary pen lifts
    optimize_order: true        # Optimize path order

# Best for:
# - Quick design reviews
# - Testing plotter operation
# - Rough drafts
# - Large simple shapes
```

#### **Quality Mode** - Maximum Quality
```yaml
# presets/quality.yaml
name: "Quality"
description: "Highest quality for final artwork"

plotting:
  motion:
    speed: 25                   # Low speed for precision
    acceleration: 1.0           # Gentle acceleration
    pen_up_height: 50           # Standard pen height
    pen_down_force: 55           # Firm pressure
    
  quality:
    precision: "ultra"          # Maximum precision
    smoothing: true             # Maximum smoothing
    corner_handling: "rounded"   # Smooth corners
    
  hardware:
    double_check: true          # Double-check movements
    slow_corners: true          # Slow down for corners

# Best for:
# - Final artwork
# - Client presentations
# - Portfolio pieces
# - Detailed designs
```

#### **Balanced Mode** - Default Performance
```yaml
# presets/balanced.yaml
name: "Balanced"
description: "Balanced speed and quality for general use"

plotting:
  motion:
    speed: 50                   # Moderate speed
    acceleration: 1.5           # Moderate acceleration
    pen_up_height: 60           # Standard pen height
    pen_down_force: 40           # Moderate pressure
    
  quality:
    precision: "medium"         # Medium precision
    smoothing: true             # Standard smoothing
    corner_handling: "smooth"    # Smooth corners

# Best for:
# - Everyday plotting
# - Standard jobs
# - Mixed complexity designs
# - Production work
```

### **Material-Specific Presets**

#### **Standard Paper**
```yaml
# presets/paper_standard.yaml
name: "Standard Paper"
description: "Optimized for standard office paper (80-100gsm)"

plotting:
  motion:
    speed: 45
    pen_down_force: 35           # Light pressure to avoid tearing
    pen_up_height: 55
    
  quality:
    precision: "medium"
    smoothing: true
    
material:
  type: "paper"
  weight_gsm: 80                # 80gsm paper
  surface: "smooth"

# Compatible pens:
# - Fine point (0.3-0.5mm)
# - Standard ballpoint
# - Gel pens
```

#### **Cardstock**
```yaml
# presets/cardstock.yaml
name: "Cardstock"
description: "Heavy cardstock and thick paper (200-300gsm)"

plotting:
  motion:
    speed: 30                   # Slower for thick material
    pen_down_force: 65           # High pressure for penetration
    pen_up_height: 70           # Higher lifts to avoid dragging
    
  quality:
    precision: "high"
    smoothing: true
    
material:
  type: "cardstock"
  weight_gsm: 250               # 250gsm cardstock
  surface: "textured"

# Compatible pens:
# - Bold point (0.7-1.0mm)
# - Permanent markers
# - Sharpie-style pens
```

#### **Vellum/Transparency**
```yaml
# presets/vellum.yaml
name: "Vellum/Transparency"
description: "Delicate transparent materials"

plotting:
  motion:
    speed: 20                   # Very slow
    pen_down_force: 20           # Very light pressure
    pen_up_height: 40           # Low lifts to avoid smudging
    
  quality:
    precision: "high"
    smoothing: true
    dry_time: 2                 # Wait 2 seconds between segments
    
material:
  type: "transparent"
  surface: "smooth"
  ink_dry_time: 5              # 5 seconds ink dry time

# Compatible pens:
# - Fine archival pens
# - Technical pens
# - Special transparency pens
```

#### **Wood/Leather**
```yaml
# presets/wood_leather.yaml
name: "Wood/Leather"
description: "Hard materials requiring engraving-style pressure"

plotting:
  motion:
    speed: 15                   # Very slow for control
    pen_down_force: 85           # Maximum pressure
    pen_up_height: 80           # High lifts
    passes: 2                   # Multiple passes
    
  quality:
    precision: "high"
    smoothing: false            # Keep sharp edges
    
material:
  type: "hard"
  hardness: "medium"
  surface: "natural"

# Compatible tools:
# - Engraving tools
# - Wood burning tips
# - Leather tools
```

### **Pen-Specific Presets**

#### **Fine Technical Pen (0.3mm)**
```yaml
# presets/pen_fine.yaml
name: "Fine Technical Pen"
description: "0.3mm technical pens for detailed work"

plotting:
  motion:
    speed: 35                   # Moderate speed
    pen_down_force: 25           # Light pressure
    pen_up_height: 50
    
  quality:
    precision: "high"           # High precision for fine lines
    smoothing: true
    min_segment_length: 0.1     # Very short segments
    
pen:
  type: "technical"
  size_mm: 0.3
  ink_type: "archival"

# Best materials:
# - Smooth paper
# - Vellum
# - Drafting film
```

#### **Bold Marker (1.0mm+)**
```yaml
# presets/pen_bold.yaml
name: "Bold Marker"
description: "1.0mm+ markers for bold graphics"

plotting:
  motion:
    speed: 60                   # Faster speed
    pen_down_force: 50           # Moderate pressure
    pen_up_height: 65
    
  quality:
    precision: "low"            # Lower precision for bold lines
    smoothing: true
    min_segment_length: 0.5     # Longer segments
    
pen:
  type: "marker"
  size_mm: 1.0
  ink_type: "alcohol"

# Best materials:
# - Cardstock
# - Poster board
# - Coated paper
```

#### **Brush Pen**
```yaml
# presets/pen_brush.yaml
name: "Brush Pen"
description: "Flexible brush pens for calligraphy"

plotting:
  motion:
    speed: 25                   # Slow for control
    pen_down_force: 35           # Variable pressure
    pen_up_height: 55
    pressure_sensitive: true     # Enable pressure control
    
  quality:
    precision: "medium"
    smoothing: true
    interpolate_pressure: true   # Smooth pressure transitions
    
pen:
  type: "brush"
  flexibility: "medium"
  ink_type: "waterbased"

# Best for:
# - Calligraphy
# - Artistic work
# - Variable line width
```

## **Custom Preset Creation**

### **Create Custom Preset**
```bash
# Create from scratch
vfab preset create my_custom_preset

# Create based on existing preset
vfab preset create --from quality my_quality_variant

# Create interactively
vfab preset create --interactive my_interactive_preset
```

### **Custom Preset Template**
```yaml
# presets/my_custom.yaml
name: "My Custom Preset"
description: "Custom settings for specific workflow"
version: "1.0"

# Plotting settings
plotting:
  motion:
    speed: 40
    acceleration: 1.5
    pen_up_height: 60
    pen_down_force: 45
    
  quality:
    precision: "medium"
    smoothing: true
    corner_handling: "smooth"
    
# Material settings
material:
  type: "custom"
  properties:
    surface_roughness: 0.3
    ink_absorption: 0.7
    
# Pen settings
pen:
  type: "custom"
  size_mm: 0.5
  properties:
    flow_rate: 0.5
    dry_time: 2

# Special settings
special:
  passes: 1
  wait_between_passes: 0
  temperature_compensation: false
  
# Metadata
metadata:
  created_by: "Your Name"
  created_date: "2024-01-01"
  suitable_for: ["art", "design", "technical"]
  tags: ["custom", "medium", "quality"]
```

### **Preset Optimization Script**
```python
# optimize_preset.py
import subprocess
import json
import time
from pathlib import Path

class PresetOptimizer:
    def __init__(self):
        self.test_design = "test_patterns/optimization_test.svg"
        self.results = []
    
    def test_preset(self, preset_name, test_file=None):
        """Test a preset and measure performance"""
        test_file = test_file or self.test_design
        
        print(f"Testing preset: {preset_name}")
        
        # Clear queue
        subprocess.run(['vfab', 'remove', '--all'], capture_output=True)
        
        # Add test job with preset
        start_time = time.time()
        result = subprocess.run([
            'vfab', 'add', '--preset', preset_name, test_file
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to add job: {result.stderr}")
            return None
        
        # Wait for completion
        subprocess.run(['vfab', 'resume'], capture_output=True)
        
        # Monitor completion
        while True:
            queue_result = subprocess.run(['vfab', 'list'], 
                                        capture_output=True, text=True)
            if len(queue_result.stdout.strip().split('\n')) <= 1:
                break
            time.sleep(2)
        
        end_time = time.time()
        plotting_time = end_time - start_time
        
        # Get quality metrics
        quality_result = subprocess.run([
            'vfab', 'check', '--quality', test_file
        ], capture_output=True, text=True)
        
        # Parse results
        metrics = {
            'preset': preset_name,
            'plotting_time': plotting_time,
            'quality_score': self.parse_quality_score(quality_result.stdout),
            'success': True
        }
        
        self.results.append(metrics)
        print(f"  Time: {plotting_time:.1f}s, Quality: {metrics['quality_score']}")
        
        return metrics
    
    def parse_quality_score(self, quality_output):
        """Parse quality score from vfab check output"""
        try:
            for line in quality_output.split('\n'):
                if 'Quality Score:' in line:
                    return float(line.split(':')[1].strip())
        except:
            pass
        return 0.0
    
    def optimize_for_speed(self, base_preset="balanced"):
        """Optimize preset for maximum speed"""
        speed_variants = [
            {'speed': 80, 'precision': 'low', 'force': 25},
            {'speed': 70, 'precision': 'low', 'force': 30},
            {'speed': 60, 'precision': 'medium', 'force': 35},
        ]
        
        print("Optimizing for speed...")
        
        for i, variant in enumerate(speed_variants):
            preset_name = f"speed_opt_{i+1}"
            
            # Create temporary preset
            self.create_temp_preset(preset_name, variant)
            
            # Test preset
            self.test_preset(preset_name)
        
        # Find best speed preset
        best_speed = min(self.results, key=lambda x: x['plotting_time'])
        print(f"Best speed preset: {best_speed['preset']} ({best_speed['plotting_time']:.1f}s)")
        
        return best_speed
    
    def optimize_for_quality(self, base_preset="balanced"):
        """Optimize preset for maximum quality"""
        quality_variants = [
            {'speed': 20, 'precision': 'ultra', 'force': 55},
            {'speed': 25, 'precision': 'high', 'force': 50},
            {'speed': 30, 'precision': 'high', 'force': 45},
        ]
        
        print("Optimizing for quality...")
        
        for i, variant in enumerate(quality_variants):
            preset_name = f"quality_opt_{i+1}"
            
            # Create temporary preset
            self.create_temp_preset(preset_name, variant)
            
            # Test preset
            self.test_preset(preset_name)
        
        # Find best quality preset
        best_quality = max(self.results, key=lambda x: x['quality_score'])
        print(f"Best quality preset: {best_quality['preset']} (score: {best_quality['quality_score']})")
        
        return best_quality
    
    def create_temp_preset(self, name, settings):
        """Create temporary preset for testing"""
        preset_content = {
            'name': name,
            'plotting': {
                'motion': {
                    'speed': settings['speed'],
                    'pen_down_force': settings['force']
                },
                'quality': {
                    'precision': settings['precision']
                }
            }
        }
        
        preset_file = Path(f"presets/{name}.yaml")
        preset_file.parent.mkdir(exist_ok=True)
        
        import yaml
        with open(preset_file, 'w') as f:
            yaml.dump(preset_content, f)
    
    def generate_optimization_report(self):
        """Generate optimization report"""
        if not self.results:
            print("No results to report")
            return
        
        report_file = f"preset_optimization_report_{int(time.time())}.txt"
        
        with open(report_file, 'w') as f:
            f.write("Preset Optimization Report\n")
            f.write("=" * 40 + "\n\n")
            
            for result in self.results:
                f.write(f"Preset: {result['preset']}\n")
                f.write(f"  Time: {result['plotting_time']:.1f}s\n")
                f.write(f"  Quality: {result['quality_score']:.2f}\n")
                f.write(f"  Efficiency: {result['quality_score']/result['plotting_time']:.3f}\n\n")
        
        print(f"Optimization report saved to {report_file}")

# Usage
if __name__ == "__main__":
    optimizer = PresetOptimizer()
    
    # Optimize for different goals
    optimizer.optimize_for_speed()
    optimizer.optimize_for_quality()
    
    # Generate report
    optimizer.generate_optimization_report()
```

## **Preset Management**

### **Preset Commands**
```bash
# List all available presets
vfab preset list
vfab preset list --detailed

# Show preset details
vfab preset show quality
vfab preset show my_custom_preset

# Create new preset
vfab preset create new_preset
vfab preset create --from quality new_quality_variant

# Edit preset
vfab preset edit my_preset
vfab preset edit --editor vim my_preset

# Delete preset
vfab preset delete old_preset

# Copy preset
vfab preset copy quality new_quality_copy

# Validate preset
vfab preset validate my_preset
vfab preset validate --all

# Export/Import presets
vfab preset export my_preset.yaml
vfab preset import downloaded_preset.yaml
```

### **Preset Categories**
```bash
# List by category
vfab preset list --category speed
vfab preset list --category material
vfab preset list --category pen

# Search presets
vfab preset search "fast"
vfab preset search "paper"
vfab preset search "fine"
```

## **Advanced Preset Features**

### **Conditional Presets**
```yaml
# presets/conditional.yaml
name: "Conditional Preset"
description: "Adaptive settings based on design complexity"

plotting:
  # Adaptive speed based on complexity
  adaptive_speed:
    enabled: true
    thresholds:
      low_complexity:    # < 1000 segments
        speed: 70
        precision: "low"
      medium_complexity: # 1000-5000 segments
        speed: 50
        precision: "medium"
      high_complexity:   # > 5000 segments
        speed: 30
        precision: "high"
  
  # Adaptive pressure based on material
  adaptive_pressure:
    enabled: true
    materials:
      paper:
        force: 35
      cardstock:
        force: 60
      vellum:
        force: 25
```

### **Multi-Stage Presets**
```yaml
# presets/multi_stage.yaml
name: "Multi-Stage Preset"
description: "Different settings for different stages"

stages:
  # First pass - outline
  outline:
    speed: 40
    pen_down_force: 35
    precision: "high"
    
  # Second pass - fill
  fill:
    speed: 60
    pen_down_force: 25
    precision: "low"
    
  # Third pass - details
  details:
    speed: 25
    pen_down_force: 45
    precision: "ultra"

# Stage assignment
stage_assignment:
  layer_1: "outline"      # Black outlines
  layer_2: "fill"          # Color fills
  layer_3: "details"       # Fine details
```

## **Related Cheat Sheets**
- [Configuration Reference](configuration.md) - Complete configuration options
- [Materials Reference](materials-reference.md) - Material-specific settings
- [Performance Tuning](../power-user/performance-tuning.md) - Advanced optimization

## **Preset Tips**
- **Start with built-ins**: Use existing presets as starting points
- **Test thoroughly**: Always test new presets on sample designs
- **Document variations**: Keep notes on what works for different scenarios
- **Version control**: Store custom presets in version control
- **Share presets**: Export and share successful presets with the community