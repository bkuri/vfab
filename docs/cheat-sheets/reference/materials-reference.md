# Materials Reference Cheat Sheet

## **Paper Materials**

### **Standard Office Paper**
```yaml
# materials/paper_standard.yaml
name: "Standard Office Paper"
description: "80-100gsm office paper"

properties:
  weight_gsm: 80-100
  thickness_mm: 0.1-0.12
  surface: "smooth"
  brightness: 92-104
  
plotting_settings:
  pen_down_force: 30-35        # Light pressure
  speed: 45-55                 # Moderate speed
  pen_up_height: 50-55         # Standard lift
  
pen_compatibility:
  - "Fine point pens (0.3-0.5mm)"
  - "Ballpoint pens"
  - "Gel pens"
  - "Rollerball pens"

tips:
  - "Use light pressure to avoid tearing"
  - "Good for testing and drafts"
  - "Inexpensive and readily available"
  - "May bleed with very wet inks"

issues:
  - "Can tear with heavy pressure"
  - "May bleed with fountain pens"
  - "Not suitable for archival work"
```

### **Premium Cardstock**
```yaml
# materials/cardstock_premium.yaml
name: "Premium Cardstock"
description: "200-300gsm premium cardstock"

properties:
  weight_gsm: 200-300
  thickness_mm: 0.25-0.35
  surface: "smooth_to_textured"
  brightness: 90-95
  
plotting_settings:
  pen_down_force: 55-70        # Heavy pressure
  speed: 25-35                 # Slower speed
  pen_up_height: 65-75         # Higher lifts
  passes: 1-2                  # Multiple passes if needed
  
pen_compatibility:
  - "Bold markers (0.7-1.0mm)"
  - "Permanent markers"
  - "Sharpie-style pens"
  - "Technical pens with firm tips"

tips:
  - "Use firm pressure for good ink transfer"
  - "Higher pen lifts prevent dragging"
  - "May require multiple passes for solid fills"
  - "Excellent for final artwork"

issues:
  - "Requires more pen pressure"
  - "Slower plotting speed"
  - "Some pens may skip on textured surfaces"
```

### **Watercolor Paper**
```yaml
# materials/paper_watercolor.yaml
name: "Watercolor Paper"
description: "140-300gsm cold press watercolor paper"

properties:
  weight_gsm: 140-300
  thickness_mm: 0.2-0.4
  surface: "textured"
  sizing: "internal_and_external"
  
plotting_settings:
  pen_down_force: 40-50        # Medium pressure
  speed: 20-30                 # Slow speed
  pen_up_height: 60-70         # Higher lifts
  dry_time: 3-5                # Wait between segments
  
pen_compatibility:
  - "Waterproof archival pens"
  - "Technical pens"
  - "Fine liners"
  - "Pigma-style pens"

tips:
  - "Use waterproof pens to prevent bleeding"
  - "Allow extra drying time"
  - "Test pens on sample first"
  - "Good for mixed media work"

issues:
  - "Texture can affect line quality"
  - "Some inks may bleed or feather"
  - "Requires careful pen selection"
```

### **Vellum/Transparency Film**
```yaml
# materials/vellum.yaml
name: "Vellum/Transparency Film"
description: "Clear or frosted transparent material"

properties:
  thickness_mm: 0.075-0.1
  surface: "smooth"
  transparency: "clear_to_frosted"
  ink_receptivity: "specialized"
  
plotting_settings:
  pen_down_force: 20-25        # Very light pressure
  speed: 15-25                 # Very slow
  pen_up_height: 40-45         # Low lifts
  dry_time: 5-10               # Extended drying time
  
pen_compatibility:
  - "Specialty transparency pens"
  - "Fine archival pens"
  - "Technical pens"
  - "Overhead projector pens"

tips:
  - "Use pens specifically designed for film"
  - "Allow ample drying time"
  - "Handle carefully to avoid smudging"
  - "Clean plotter bed frequently"

issues:
  - "Ink takes longer to dry"
  - "Easily smudged"
  - "Limited pen compatibility"
  - "Static can attract dust"
```

## **Specialty Materials**

### **Wood Surfaces**
```yaml
# materials/wood.yaml
name: "Wood"
description: "Light-colored wood surfaces"

properties:
  hardness: "soft_to_medium"
  grain: "present"
  surface: "natural"
  porosity: "medium"
  
plotting_settings:
  pen_down_force: 75-90        # Very heavy pressure
  speed: 10-20                 # Very slow
  pen_up_height: 75-85         # High lifts
  passes: 2-3                  # Multiple passes
  
tool_compatibility:
  - "Wood burning tools"
  - "Engraving tools"
  - "Specialized wood markers"
  - "Pyrography tips"

tips:
  - "Sand surface smooth before plotting"
  - "Test on scrap piece first"
  - "Use appropriate safety equipment"
  - "Consider wood grain direction"

issues:
  - "Requires specialized tools"
  - "Can damage plotter if done incorrectly"
  - "Produces dust/debris"
  - "Requires safety precautions"
```

### **Leather**
```yaml
# materials/leather.yaml
name: "Leather"
description: "Vegetable-tanned leather"

properties:
  thickness_mm: 1-3
  surface: "natural_textured"
  porosity: "low"
  flexibility: "medium"
  
plotting_settings:
  pen_down_force: 70-85        # Heavy pressure
  speed: 15-25                 # Slow speed
  pen_up_height: 70-80         # High lifts
  passes: 2                    # Multiple passes
  
tool_compatibility:
  - "Leather engraving tools"
  - "Specialized leather markers"
  - "Pyrography tools"
  - "Leather stamps"

tips:
  - "Clean surface thoroughly"
  - "Test on scrap piece"
  - "Use leather-specific tools"
  - "Consider finish type"

issues:
  - "Requires specialized tools"
  - "Surface preparation critical"
  - "Limited color options"
  - "Can be expensive to test"
```

### **Acrylic/Plexiglass**
```yaml
# materials/acrylic.yaml
name: "Acrylic/Plexiglass"
description: "Clear or colored acrylic sheets"

properties:
  thickness_mm: 2-6
  surface: "smooth"
  hardness: "hard"
  transparency: "clear_to_opaque"
  
plotting_settings:
  pen_down_force: 60-80        # Heavy pressure
  speed: 20-30                 # Slow speed
  pen_up_height: 65-75         # High lifts
  passes: 1-2                  # Multiple passes
  
tool_compatibility:
  - "Acrylic engraving tools"
  - "Specialized acrylic markers"
  - "Diamond tip tools"
  - "Rotary tools"

tips:
  - "Remove protective film"
  - "Use proper ventilation"
  - "Secure material firmly"
  - "Test on scrap piece"

issues:
  - "Can crack under pressure"
  - "Requires specialized tools"
  - "Creates fine dust"
  - "Safety equipment required"
```

## **Pen and Ink Compatibility**

### **Pen Types by Material**

#### **Fine Technical Pens (0.1-0.3mm)**
```yaml
# pens/technical_fine.yaml
best_materials:
  - "Vellum/Transparency"
  - "Smooth paper"
  - "Drafting film"
  - "Bristol board"

settings:
  pressure: "light"
  speed: "slow_to_moderate"
  
recommended_inks:
  - "Archival pigment ink"
  - "Waterproof ink"
  - "Fast-drying ink"

avoid:
  - "Textured papers"
  - "Very absorbent materials"
  - "Thick cardstock"
```

#### **Medium Point Pens (0.5-0.7mm)**
```yaml
# pens/technical_medium.yaml
best_materials:
  - "Standard paper"
  - "Cardstock"
  - "Bristol board"
  - "Mixed media paper"

settings:
  pressure: "medium"
  speed: "moderate"
  
recommended_inks:
  - "Pigment ink"
  - "Waterproof ink"
  - "Gel ink"

good_for:
  - "General purpose plotting"
  - "Technical drawings"
  - "Artwork"
```

#### **Bold Markers (1.0mm+)**
```yaml
# pens/bold_markers.yaml
best_materials:
  - "Cardstock"
  - "Poster board"
  - "Foam board"
  - "Coated papers"

settings:
  pressure: "firm"
  speed: "moderate_to_fast"
  
recommended_inks:
  - "Alcohol-based ink"
  - "Permanent ink"
  - "Oil-based ink"

applications:
  - "Bold graphics"
  - "Posters"
  - "Signage"
  - "Large format work"
```

#### **Brush Pens**
```yaml
# pens/brush.yaml
best_materials:
  - "Smooth paper"
  - "Mixed media paper"
  - "Watercolor paper"
  - "Bristol board"

settings:
  pressure: "variable"
  speed: "slow"
  special_features: "pressure_sensitive"

techniques:
  - "Calligraphy"
  - "Variable line width"
  - "Artistic effects"
  - "Expressive work"

challenges:
  - "Requires pressure control"
  - "Slower plotting"
  - "Ink flow management"
```

## **Material Testing Protocol**

### **Test Pattern Generator**
```python
# material_test.py
import vsketch
from pathlib import Path

class MaterialTestGenerator:
    def __init__(self):
        self.test_patterns = {
            'line_quality': self.generate_line_test,
            'pressure_test': self.generate_pressure_test,
            'speed_test': self.generate_speed_test,
            'detail_test': self.generate_detail_test,
            'bleed_test': self.generate_bleed_test
        }
    
    def generate_line_test(self, vsk):
        """Generate line quality test"""
        vsk.size("a4", center=True)
        
        # Horizontal lines
        for i in range(10):
            y = -100 + i * 20
            vsk.stroke(1)
            vsk.line(-100, y, 100, y)
        
        # Vertical lines
        for i in range(10):
            x = -90 + i * 20
            vsk.stroke(1)
            vsk.line(x, -100, x, 100)
        
        # Diagonal lines
        for i in range(5):
            offset = i * 20
            vsk.stroke(1)
            vsk.line(-100 + offset, -100, 100 + offset, 100)
            vsk.line(100 - offset, -100, -100 - offset, 100)
    
    def generate_pressure_test(self, vsk):
        """Generate pressure test pattern"""
        vsk.size("a4", center=True)
        
        # Pressure gradient test
        for i in range(10):
            y = -80 + i * 16
            vsk.stroke(1)
            # Different line weights to simulate pressure
            for j in range(5):
                x = -80 + j * 40
                vsk.circle(x, y, 2 + j)
    
    def generate_speed_test(self, vsk):
        """Generate speed test pattern"""
        vsk.size("a4", center=True)
        
        # Test different curve complexities
        for i in range(5):
            y = -60 + i * 30
            vsk.stroke(1)
            
            # Simple to complex curves
            points = []
            for x in range(-80, 81, 10):
                freq = 0.1 + i * 0.05
                y_offset = 20 * (i + 1) * 0.2
                points.append((x, y + y_offset * (x/80) * freq))
            
            vsk.polygon(points)
    
    def generate_detail_test(self, vsk):
        """Generate detail test pattern"""
        vsk.size("a4", center=True)
        
        # Fine details
        for i in range(20):
            for j in range(20):
                x = -90 + i * 9
                y = -90 + j * 9
                size = 1 + (i + j) % 3
                vsk.stroke(1)
                vsk.circle(x, y, size)
        
        # Text test
        vsk.stroke(1)
        vsk.text("Test Text 123", -50, 0, size=10)
    
    def generate_bleed_test(self, vsk):
        """Generate ink bleed test"""
        vsk.size("a4", center=True)
        
        # Close parallel lines
        for i in range(20):
            y = -50 + i * 5
            vsk.stroke(1)
            vsk.line(-80, y, 80, y)
        
        # Dense crosshatch
        for i in range(-40, 41, 4):
            vsk.stroke(1)
            vsk.line(i, -40, i, 40)
            vsk.line(-40, i, 40, i)
    
    def create_test_suite(self, output_dir="material_tests"):
        """Create complete test suite"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for test_name, test_func in self.test_patterns.items():
            vsk = vsketch.Vsketch()
            test_func(vsk)
            
            filename = f"{test_name}_test.svg"
            filepath = output_path / filename
            vsk.save(str(filepath))
            
            print(f"Created {filename}")

# Usage
if __name__ == "__main__":
    generator = MaterialTestGenerator()
    generator.create_test_suite()
```

### **Material Test Results Template**
```yaml
# material_test_results.yaml
material_name: "Test Material"
test_date: "2024-01-01"
tester: "Your Name"

test_results:
  line_quality:
    rating: 1-5
    notes: "Notes about line smoothness, consistency"
    issues: ["Any issues observed"]
    
  pressure_response:
    rating: 1-5
    notes: "How well does material respond to pressure?"
    optimal_pressure: "Recommended pressure setting"
    
  speed_tolerance:
    rating: 1-5
    max_speed: "Maximum speed without quality loss"
    notes: "Speed-related observations"
    
  detail_capability:
    rating: 1-5
    min_line_width: "Minimum reliable line width"
    notes: "Detail reproduction quality"
    
  ink_bleed:
    rating: 1-5
    notes: "Ink bleeding observations"
    dry_time: "Time until ink is dry"

recommendations:
  best_pen_types: ["Recommended pen types"]
  optimal_settings:
    speed: "Recommended speed"
    pressure: "Recommended pressure"
    passes: "Number of passes if needed"
  
  applications: ["Suitable applications"]
  limitations: ["Known limitations"]

overall_rating: 1-5
would_recommend: true/false
```

## **Material Database**

### **Add Custom Material**
```bash
# Add new material to database
plotty material add custom_material.yaml

# Test material with standard patterns
plotty material test custom_material --all-tests

# Compare materials
plotty material compare material1 material2

# List all materials
plotty material list
plotty material list --category paper
```

### **Material Properties Database**
```python
# material_database.py
import json
from pathlib import Path

class MaterialDatabase:
    def __init__(self, db_file="materials_database.json"):
        self.db_file = Path(db_file)
        self.materials = self.load_database()
    
    def load_database(self):
        """Load materials database"""
        if self.db_file.exists():
            with open(self.db_file) as f:
                return json.load(f)
        return {}
    
    def save_database(self):
        """Save materials database"""
        with open(self.db_file, 'w') as f:
            json.dump(self.materials, f, indent=2)
    
    def add_material(self, material_data):
        """Add new material to database"""
        name = material_data['name']
        self.materials[name] = material_data
        self.save_database()
        print(f"Added material: {name}")
    
    def find_materials_by_property(self, property_name, value_range):
        """Find materials by property range"""
        matches = []
        
        for name, material in self.materials.items():
            if property_name in material.get('properties', {}):
                prop_value = material['properties'][property_name]
                
                # Handle range values
                if isinstance(prop_value, str) and '-' in prop_value:
                    min_val, max_val = map(float, prop_value.split('-'))
                    if min_val <= value_range <= max_val:
                        matches.append(name)
                elif isinstance(prop_value, (int, float)):
                    if prop_value == value_range:
                        matches.append(name)
        
        return matches
    
    def recommend_materials(self, requirements):
        """Recommend materials based on requirements"""
        recommendations = []
        
        for name, material in self.materials.items():
            score = 0
            
            # Check weight requirements
            if 'weight_gsm' in requirements:
                if 'weight_gsm' in material.get('properties', {}):
                    score += 1
            
            # Check surface requirements
            if 'surface' in requirements:
                if material.get('properties', {}).get('surface') == requirements['surface']:
                    score += 2
            
            # Check pen compatibility
            if 'pen_type' in requirements:
                if requirements['pen_type'] in material.get('pen_compatibility', []):
                    score += 2
            
            if score > 0:
                recommendations.append((name, score))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [name for name, score in recommendations]
    
    def generate_material_report(self, material_name):
        """Generate detailed material report"""
        if material_name not in self.materials:
            print(f"Material '{material_name}' not found")
            return None
        
        material = self.materials[material_name]
        
        report = f"""
Material Report: {material_name}
{'=' * 50}

Description: {material.get('description', 'No description')}

Properties:
"""
        
        for prop, value in material.get('properties', {}).items():
            report += f"  {prop}: {value}\n"
        
        report += "\nPlotting Settings:\n"
        for setting, value in material.get('plotting_settings', {}).items():
            report += f"  {setting}: {value}\n"
        
        report += "\nCompatible Pens:\n"
        for pen in material.get('pen_compatibility', []):
            report += f"  - {pen}\n"
        
        report += "\nTips:\n"
        for tip in material.get('tips', []):
            report += f"  - {tip}\n"
        
        if 'issues' in material:
            report += "\nPotential Issues:\n"
            for issue in material['issues']:
                report += f"  - {issue}\n"
        
        return report

# Usage
if __name__ == "__main__":
    db = MaterialDatabase()
    
    # Find materials by weight
    lightweight_materials = db.find_materials_by_property('weight_gsm', 90)
    print(f"Lightweight materials: {lightweight_materials}")
    
    # Get recommendations
    requirements = {
        'weight_gsm': '80-120',
        'surface': 'smooth',
        'pen_type': 'Fine technical pens'
    }
    recommendations = db.recommend_materials(requirements)
    print(f"Recommended materials: {recommendations}")
    
    # Generate report
    report = db.generate_material_report("Standard Office Paper")
    print(report)
```

## **Related Cheat Sheets**
- [Optimization Presets](optimization-presets.md) - Material-specific presets
- [Configuration Reference](configuration.md) - Material configuration options
- [Design Optimization](../creative/design-optimization.md) - Material-aware design

## **Material Tips**
- **Test first**: Always test new materials with sample patterns
- **Document results**: Keep detailed notes on material performance
- **Start conservative**: Begin with lower pressure and speed
- **Consider environment**: Temperature and humidity affect results
- **Safety first**: Use appropriate safety equipment for specialty materials