# Design Optimization Cheat Sheet

## **Quick Optimization Checklist**

### **Before Plotting**
```bash
# Check design complexity
vfab check my_design.svg

# Estimate plotting time
vfab info my_design.svg

# Test with dry run
vfab add --dry-run my_design.svg
```

## **Path Optimization**

### **Reduce Pen Lifts**
```python
# Bad: Many separate shapes
for x in range(10):
    for y in range(10):
        vsk.circle(x * 20, y * 20, 5)

# Good: Connect when possible
points = []
for x in range(10):
    for y in range(10):
        points.extend([(x * 20, y * 20), (x * 20, y * 20)])  # Duplicate for closed path
vsk.polygon(points)
```

### **Optimize Stroke Order**
```python
# Group by location to minimize travel
shapes_by_region = group_shapes_by_location(all_shapes)

for region in sorted_regions_by_proximity(shapes_by_region):
    for shape in region.shapes:
        draw_shape(shape)
```

### **Merge Nearby Paths**
```bash
# Use vpype to optimize paths
vpype read my_design.svg \
      linemerge --tolerance 0.5mm \
      linesort \
      write optimized_design.svg

# Check improvement
vfab check my_design.svg
vfab check optimized_design.svg
```

## **Complexity Reduction**

### **Detail Level Adjustment**
```python
# High detail (slow)
vsk.detail("0.1mm")

# Medium detail (balanced)
vsk.detail("0.3mm")  

# Low detail (fast)
vsk.detail("0.5mm")
```

### **Curve Simplification**
```bash
# Simplify complex curves
vpype read complex_design.svg \
      simplify --tolerance 0.2mm \
      write simplified_design.svg

# Compare file sizes
ls -lh complex_design.svg simplified_design.svg
```

### **Remove Redundant Points**
```python
# Filter collinear points
def simplify_path(points, tolerance=0.1):
    simplified = [points[0]]
    for i in range(1, len(points) - 1):
        if distance_to_line(points[i], points[i-1], points[i+1]) > tolerance:
            simplified.append(points[i])
    simplified.append(points[-1])
    return simplified
```

## **Layer Strategy**

### **Organize by Pen**
```python
# Group similar elements together
vsk.stroke(1)  # Black outlines
draw_all_outlines()

vsk.stroke(2)  # Red fills  
draw_all_fills()

vsk.stroke(3)  # Blue details
draw_all_details()
```

### **Minimize Pen Changes**
```bash
# Check layer distribution
vfab info multilayer_design.svg

# Reorder layers if needed
vpype read design.svg \
      layer --copy 1 4  # Copy layer 1 to 4
      layer --remove 1  # Remove original
      write reordered_design.svg
```

## **Size and Scaling**

### **Optimal Sizing**
```python
# Standard paper sizes with margins
def safe_area(paper_size, margin_mm=10):
    widths = {"a4": 210, "a3": 297, "letter": 216}
    heights = {"a4": 297, "a3": 420, "letter": 279}
    
    w = widths[paper_size.lower()] - 2 * margin_mm
    h = heights[paper_size.lower()] - 2 * margin_mm
    return w, h

# Use safe area
w, h = safe_area("a4")
vsk.size(f"{w}mm", f"{h}mm", center=False)
```

### **Smart Scaling**
```bash
# Scale to fit while maintaining aspect ratio
vpype read large_design.svg \
      scale --fit a4 --margin 10mm \
      write scaled_design.svg

# Check plotting time improvement
vfab info large_design.svg
vfab info scaled_design.svg
```

## **Performance Testing**

### **Benchmark Your Designs**
```bash
# Create test variations
for scale in 0.5 0.75 1.0 1.25; do
    vpype read base_design.svg \
          scale $scale \
          write test_${scale}.svg
done

# Compare performance
for file in test_*.svg; do
    echo "=== $file ==="
    vfab check "$file"
done
```

### **Time vs Quality Trade-offs**
```python
# Generate quality test matrix
def quality_test_matrix():
    qualities = ["0.1mm", "0.3mm", "0.5mm", "1.0mm"]
    scales = [0.5, 0.75, 1.0]
    
    for quality in qualities:
        for scale in scales:
            filename = f"test_q{quality}_s{scale}.svg"
            generate_test_design(filename, quality, scale)
```

## **Material-Specific Optimization**

### **Paper Type Optimization**
```python
# Thin paper (gentle settings)
thin_paper_settings = {
    "pen_speed": 20,
    "pen_force": 30,
    "detail_level": "0.5mm"
}

# Thick paper (bolder settings)
thick_paper_settings = {
    "pen_speed": 40,
    "pen_force": 60,
    "detail_level": "0.3mm"
}
```

### **Pen Type Considerations**
```bash
# Fine pen (0.3mm) - use less detail
vfab add --preset fine-pen detailed_design.svg

# Bold pen (1.0mm) - can handle more detail
vfab add --preset bold-pen detailed_design.svg
```

## **Automated Optimization Pipeline**

### **Pre-Flight Checklist**
```bash
#!/bin/bash
# optimize_design.sh

design_file=$1

echo "Optimizing $design_file..."

# 1. Check original
echo "Original design:"
vfab check "$design_file"

# 2. Optimize paths
vpype read "$design_file" \
      linemerge --tolerance 0.3mm \
      linesort \
      simplify --tolerance 0.2mm \
      write "optimized_$design_file"

# 3. Check optimized version
echo "Optimized design:"
vfab check "optimized_$design_file"

# 4. Generate comparison
echo "Improvement:"
diff -u <(vfab check "$design_file") <(vfab check "optimized_$design_file")
```

### **Batch Optimization**
```bash
# Optimize entire directory
for svg in designs/*.svg; do
    echo "Optimizing $svg..."
    vpype read "$svg" \
          linemerge --tolerance 0.3mm \
          linesort \
          write "optimized/$(basename "$svg")"
done
```

## **Troubleshooting Performance**

### **Common Bottlenecks**
```bash
# Check for excessive points
vpype read slow_design.svg \
      stats --details

# Find tiny segments
vpype read slow_design.svg \
      filter --length-min 0.1mm \
      stats

# Remove very short segments
vpype read slow_design.svg \
      filter --length-min 0.5mm \
      write cleaned_design.svg
```

### **Memory Issues**
```bash
# Process large files in chunks
vpype read huge_design.svg \
      split --pages a4 \
      write page_%d.svg

# Process each page individually
for page in page_*.svg; do
    vfab add "$page"
done
```

## **Quality Assurance**

### **Pre-Plot Validation**
```bash
# Comprehensive design check
validate_design() {
    local file=$1
    
    echo "=== Validating $file ==="
    
    # Check file integrity
    vfab check "$file" || return 1
    
    # Estimate time
    vfab info "$file" | grep "Estimated"
    
    # Test dry run
    vfab add --dry-run "$file" || return 1
    
    echo "✓ Design validation passed"
}
```

### **Visual Verification**
```bash
# Generate preview
vpype read final_design.svg \
      show  # Display preview

# Create test plot on paper
vfab add --test-mode final_design.svg
```

## **Related Cheat Sheets**
- [vsketch Integration](vsketch-integration.md) - Generate optimized designs programmatically
- [Batch Production](../power-user/batch-production.md) - Scale up optimized designs
- [Configuration Reference](../reference/configuration.md) - Performance-related settings

## **Optimization Tools**
- **vpype**: Powerful vector processing pipeline
- **vfab check**: Built-in design validation
- **vfab info**: Performance estimation
- **Custom scripts**: Automate your optimization workflow