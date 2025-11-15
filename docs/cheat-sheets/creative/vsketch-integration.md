# vsketch Integration Cheat Sheet

## 🧭 Quick Navigation
- **New to vfab?** [First Plot Checklist](../beginner/first-plot-checklist.md)
- **Multi-pen designs?** [Multi-Pen Workflow](multi-pen-workflow.md)
- **Optimize your designs?** [Design Optimization](design-optimization.md)
- **Generate many designs?** [Batch Art Generation](batch-art-generation.md)

---

## **Quick Setup**
```bash
# Install vsketch with vfab support
pip install vsketch

# Initialize vsketch project
vsk new my_plotting_project
cd my_plotting_project

# Configure vfab as plotter backend
vsk set plotter vfab
```

## **Basic vsketch → vfab Workflow**

### **1. Create Your Sketch**
```python
# sketch.py
import vsketch

class MySketch(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch):
        vsk.size("a4")
        vsk.detail("0.1mm")
        
        # Draw some shapes
        for i in range(10):
            vsk.circle(i * 20, 0, 5 + i)
        
        vsk.polygon([(-50, -50), (50, -50), (0, 50)])

if __name__ == "__main__":
    MySketch().display()
```

### **2. Send to vfab**
```bash
# Preview and send to vfab
vsk run --save final.svg
vfab add final.svg

# Or direct pipeline
vsk run --save - | vfab add -
```

## **Advanced Integration**

### **Batch Processing**
```python
# Generate multiple variations
import vsketch
import random

def generate_variation(seed):
    vsk = vsketch.Vsketch()
    vsk.size("a4", center=False)
    random.seed(seed)
    
    # Your generative code here
    for i in range(20):
        x = random.uniform(0, 210)
        y = random.uniform(0, 297)
        r = random.uniform(5, 20)
        vsk.circle(x, y, r)
    
    return vsk

# Create batch
for seed in range(5):
    sketch = generate_variation(seed)
    sketch.save(f"variation_{seed}.svg")
    vfab add f"variation_{seed}.svg"
```

### **vfab Presets in vsketch**
```python
# Use vfab presets in your sketch
import vsketch

class PresetSketch(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch):
        # Configure for vfab preset
        vsk.size("a4")
        vsk.penWidth("0.3mm")  # Matches vfab pen settings
        
        # Draw with preset-aware parameters
        vsk.stroke(1)  # Layer 1 for first pen
        # ... drawing code ...
        
        vsk.stroke(2)  # Layer 2 for second pen
        # ... more drawing code ...
```

## **Parameter Sweeps**

### **Create Parameterized Designs**
```python
# parametric_sketch.py
import vsketch
import numpy as np

class ParametricSketch(vsketch.SketchClass):
    # Define parameters
    count = vsketch.Param(10, min=1, max=50, step=1)
    radius = vsketch.Param(50, min=10, max=100, step=5)
    layers = vsketch.Param(3, min=1, max=8, step=1)
    
    def draw(self, vsk: vsketch.Vsketch):
        vsk.size("a4", center=True)
        
        for layer in range(self.layers):
            vsk.stroke(layer + 1)
            for i in range(self.count):
                angle = (i / self.count) * 2 * np.pi
                x = np.cos(angle) * self.radius
                y = np.sin(angle) * self.radius
                vsk.circle(x, y, 10)
```

### **Generate and Queue Variations**
```bash
# Generate parameter sweep
vsk run --param count=20 --param radius=60 --save sweep_1.svg
vsk run --param count=30 --param radius=80 --save sweep_2.svg
vsk run --param count=40 --param radius=100 --save sweep_3.svg

# Add all to vfab
vfab add sweep_*.svg

# Check status
vfab list
```

## **Real-world Workflows**

### **Generative Art Pipeline**
```bash
# 1. Generate designs
python generate_designs.py  # Creates 20 variations

# 2. Review and select
vfab list  # See all queued designs
vfab info design_05.svg  # Check specific design

# 3. Plot selected ones
vfab resume  # Start plotting
```

### **Iterative Design Process**
```bash
# Design loop
while true; do
    # Edit sketch.py
    vim sketch.py
    
    # Test preview
    vsk run --preview
    
    # If happy, add to queue
    read -p "Add to queue? (y/n) " answer
    if [[ $answer == "y" ]]; then
        vsk run --save iteration_$(date +%H%M).svg
        vfab add iteration_$(date +%H%M).svg
    fi
done
```

## **Troubleshooting vsketch + vfab**

### **Common Issues**
```bash
# Check vfab status
vfab info

# Verify SVG compatibility
vfab check my_design.svg

# Clear queue if needed
vfab remove --all

# Restart vfab service
sudo systemctl restart vfabd
```

### **File Format Issues**
```python
# Ensure proper SVG output
vsk.size("a4", landscape=False)  # Explicit orientation
vsk.detail("0.1mm")  # Set appropriate detail level
vsk.penWidth("0.3mm")  # Match vfab pen widths
```

## **Pro Tips**

### **Layer Management**
```python
# Use vfab layer system
vsk.stroke(1)  # First pen/color
# Draw elements for pen 1

vsk.stroke(2)  # Second pen/color  
# Draw elements for pen 2
```

### **Performance Optimization**
```python
# Reduce complexity for faster plotting
vsk.detail("0.5mm")  # Lower detail = faster
vsk.scale("50%")     # Smaller = faster
```

### **Batch Export**
```bash
# Export all variations at once
for i in {1..10}; do
    vsk run --param seed=$i --save "design_${i}.svg"
done

# Add to vfab in bulk
vfab add design_*.svg
```

## **Related Cheat Sheets**
- [Multi-Pen Workflow](multi-pen-workflow.md) - Hardware setup for multi-pen plotting
- [Design Optimization](design-optimization.md) - Optimize designs for plotting
- [Batch Production](../power-user/batch-production.md) - Professional batch workflows

## **Integration Examples**
See `examples/vsketch/` directory for complete working examples of:
- Generative patterns
- Parameterized designs  
- Multi-layer artwork
- Batch processing scripts