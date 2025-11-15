# Batch Art Generation Cheat Sheet

## **Quick Batch Setup**

### **Initialize Batch Project**
```bash
# Create batch generation directory
mkdir batch_art_project
cd batch_art_project

# Set up vfab workspace
vfab init

# Create generation script
touch generate_batch.py
```

## **Generative Systems**

### **Parameterized Art Generator**
```python
# generate_batch.py
import vsketch
import random
import numpy as np
from pathlib import Path

class BatchArtGenerator:
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_variation(self, seed, params):
        """Generate single art variation"""
        vsk = vsketch.Vsketch()
        vsk.size("a4", center=True)
        
        random.seed(seed)
        np.random.seed(seed)
        
        # Your generative algorithm here
        self.draw_pattern(vsk, params)
        
        return vsk
    
    def draw_pattern(self, vsk, params):
        """Example: Generative circles pattern"""
        num_circles = params.get('circles', 20)
        max_radius = params.get('max_radius', 30)
        
        for i in range(num_circles):
            x = random.uniform(-100, 100)
            y = random.uniform(-140, 140)
            r = random.uniform(5, max_radius)
            
            # Layer by size
            layer = 1 if r > 20 else 2
            vsk.stroke(layer)
            vsk.circle(x, y, r)
    
    def generate_batch(self, count, param_ranges):
        """Generate batch of variations"""
        generated = []
        
        for i in range(count):
            # Randomize parameters
            params = {}
            for key, (min_val, max_val) in param_ranges.items():
                params[key] = random.uniform(min_val, max_val)
            
            # Generate art
            seed = random.randint(0, 1000000)
            vsk = self.generate_variation(seed, params)
            
            # Save with metadata
            filename = f"art_{i:04d}_seed{seed}.svg"
            filepath = self.output_dir / filename
            vsk.save(str(filepath))
            
            # Save metadata
            metadata = {
                'seed': seed,
                'params': params,
                'filename': filename
            }
            generated.append(metadata)
            
            print(f"Generated {filename}")
        
        return generated

# Usage
if __name__ == "__main__":
    generator = BatchArtGenerator()
    
    # Define parameter ranges
    param_ranges = {
        'circles': (10, 50),
        'max_radius': (15, 40)
    }
    
    # Generate batch
    batch_metadata = generator.generate_batch(20, param_ranges)
    
    # Save batch metadata
    import json
    with open('batch_metadata.json', 'w') as f:
        json.dump(batch_metadata, f, indent=2)
    
    print(f"Generated {len(batch_metadata)} artworks")
```

### **Evolutionary Art System**
```python
# evolutionary_generator.py
import vsketch
import random
import copy
from pathlib import Path

class ArtworkDNA:
    def __init__(self):
        self.genes = {
            'complexity': random.uniform(0.1, 1.0),
            'symmetry': random.uniform(0, 1),
            'density': random.uniform(0.1, 1.0),
            'style': random.choice(['geometric', 'organic', 'mixed'])
        }
    
    def mutate(self, mutation_rate=0.1):
        """Create mutated version"""
        child = copy.deepcopy(self)
        
        for gene in child.genes:
            if random.random() < mutation_rate:
                if isinstance(child.genes[gene], float):
                    child.genes[gene] += random.uniform(-0.2, 0.2)
                    child.genes[gene] = max(0, min(1, child.genes[gene]))
                else:
                    child.genes[gene] = random.choice(['geometric', 'organic', 'mixed'])
        
        return child
    
    def crossover(self, other):
        """Combine with another DNA"""
        child = ArtworkDNA()
        for gene in child.genes:
            child.genes[gene] = random.choice([self.genes[gene], other.genes[gene]])
        return child

class EvolutionaryGenerator:
    def __init__(self, population_size=10):
        self.population_size = population_size
        self.population = [ArtworkDNA() for _ in range(population_size)]
        self.generation = 0
    
    def generate_from_dna(self, dna, filename):
        """Generate artwork from DNA"""
        vsk = vsketch.Vsketch()
        vsk.size("a4", center=True)
        
        # Interpret DNA as visual parameters
        if dna.genes['style'] == 'geometric':
            self.draw_geometric(vsk, dna)
        elif dna.genes['style'] == 'organic':
            self.draw_organic(vsk, dna)
        else:
            self.draw_mixed(vsk, dna)
        
        vsk.save(filename)
        return filename
    
    def draw_geometric(self, vsk, dna):
        """Generate geometric pattern"""
        num_shapes = int(10 + dna.genes['complexity'] * 40)
        
        for i in range(num_shapes):
            x = random.uniform(-100, 100)
            y = random.uniform(-140, 140)
            size = 5 + dna.genes['density'] * 25
            
            vsk.stroke(1)
            if random.random() < dna.genes['symmetry']:
                # Symmetric shapes
                vsk.rect(x, y, size, size)
                vsk.rect(-x, y, size, size)
            else:
                vsk.circle(x, y, size)
    
    def evolve_generation(self):
        """Create next generation"""
        self.generation += 1
        
        # Select best (random for demo)
        selected = random.sample(self.population, min(5, len(self.population)))
        
        # Create next generation
        new_population = []
        for i in range(self.population_size):
            if i < len(selected):
                new_population.append(selected[i])  # Keep elites
            else:
                parent1, parent2 = random.sample(selected, 2)
                child = parent1.crossover(parent2).mutate()
                new_population.append(child)
        
        self.population = new_population
    
    def generate_evolution_batch(self, generations=5):
        """Generate evolutionary batch"""
        output_dir = Path("evolution_output")
        output_dir.mkdir(exist_ok=True)
        
        for gen in range(generations):
            print(f"Generation {gen + 1}")
            
            # Generate all individuals in current generation
            for i, dna in enumerate(self.population):
                filename = output_dir / f"gen{gen+1}_ind{i+1}.svg"
                self.generate_from_dna(dna, str(filename))
            
            # Evolve to next generation (except last)
            if gen < generations - 1:
                self.evolve_generation()
        
        print(f"Generated {generations * self.population_size} artworks")

# Usage
if __name__ == "__main__":
    evo_gen = EvolutionaryGenerator(population_size=8)
    evo_gen.generate_evolution_batch(generations=6)
```

## **Automated Curation**

### **Quality Assessment**
```python
# quality_filter.py
import vsketch
import json
from pathlib import Path

class ArtworkCurator:
    def __init__(self):
        self.quality_metrics = {}
    
    def analyze_artwork(self, filepath):
        """Analyze artwork for quality metrics"""
        # Read SVG and extract features
        vsk = vsketch.Vsketch()
        # Note: This is a simplified example
        
        metrics = {
            'complexity': self.calculate_complexity(filepath),
            'balance': self.calculate_balance(filepath),
            'coverage': self.calculate_coverage(filepath),
            'layer_usage': self.analyze_layers(filepath)
        }
        
        # Calculate overall quality score
        quality_score = self.calculate_quality_score(metrics)
        metrics['quality_score'] = quality_score
        
        return metrics
    
    def calculate_complexity(self, filepath):
        """Estimate visual complexity"""
        # Count paths, points, etc.
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Simple heuristic: count path elements
        path_count = content.count('<path')
        circle_count = content.count('<circle')
        rect_count = content.count('<rect')
        
        return (path_count + circle_count + rect_count) / 100.0  # Normalize
    
    def calculate_quality_score(self, metrics):
        """Calculate overall quality score"""
        # Weight different metrics
        weights = {
            'complexity': 0.3,
            'balance': 0.25,
            'coverage': 0.25,
            'layer_usage': 0.2
        }
        
        score = 0
        for metric, weight in weights.items():
            # Normalize metrics to 0-1 range
            value = min(1.0, max(0.0, metrics[metric]))
            score += value * weight
        
        return score
    
    def curate_batch(self, input_dir, output_dir, threshold=0.5):
        """Filter batch by quality"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        curated = []
        rejected = []
        
        for svg_file in input_path.glob("*.svg"):
            metrics = self.analyze_artwork(svg_file)
            
            if metrics['quality_score'] >= threshold:
                # Copy to curated directory
                import shutil
                shutil.copy2(svg_file, output_path / svg_file.name)
                curated.append({
                    'filename': svg_file.name,
                    'metrics': metrics
                })
            else:
                rejected.append({
                    'filename': svg_file.name,
                    'metrics': metrics
                })
        
        # Save curation report
        report = {
            'threshold': threshold,
            'curated_count': len(curated),
            'rejected_count': len(rejected),
            'curated': curated,
            'rejected': rejected
        }
        
        with open(output_path / 'curation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Curated {len(curated)} artworks, rejected {len(rejected)}")
        return report

# Usage
if __name__ == "__main__":
    curator = ArtworkCurator()
    report = curator.curate_batch("output", "curated_output", threshold=0.6)
```

## **Batch Processing Pipeline**

### **Complete Pipeline Script**
```bash
#!/bin/bash
# batch_pipeline.sh

set -e

# Configuration
BATCH_SIZE=50
OUTPUT_DIR="batch_$(date +%Y%m%d_%H%M%S)"
QUALITY_THRESHOLD=0.5

echo "Starting batch art generation..."
echo "Output directory: $OUTPUT_DIR"

# 1. Generate batch
echo "Step 1: Generating $BATCH_SIZE artworks..."
python generate_batch.py --count $BATCH_SIZE --output "$OUTPUT_DIR/raw"

# 2. Quality assessment
echo "Step 2: Assessing quality..."
python quality_filter.py --input "$OUTPUT_DIR/raw" --output "$OUTPUT_DIR/curated" --threshold $QUALITY_THRESHOLD

# 3. Add to vfab queue
echo "Step 3: Adding curated artworks to vfab queue..."
for svg in "$OUTPUT_DIR/curated"/*.svg; do
    vfab add "$svg"
done

# 4. Generate report
echo "Step 4: Generating batch report..."
vfab list > "$OUTPUT_DIR/queue_status.txt"

echo "Batch pipeline complete!"
echo "Queue status:"
vfab list
```

### **Parallel Generation**
```python
# parallel_generator.py
import multiprocessing as mp
import vsketch
from pathlib import Path

def generate_single_worker(args):
    """Worker function for parallel generation"""
    index, seed, params, output_dir = args
    
    vsk = vsketch.Vsketch()
    vsk.size("a4", center=True)
    
    # Generate artwork (simplified)
    random.seed(seed)
    
    for i in range(params.get('elements', 20)):
        x = random.uniform(-100, 100)
        y = random.uniform(-140, 140)
        vsk.circle(x, y, random.uniform(5, 20))
    
    filename = f"parallel_{index:04d}.svg"
    filepath = Path(output_dir) / filename
    vsk.save(str(filepath))
    
    return filename

class ParallelBatchGenerator:
    def __init__(self, num_processes=None):
        self.num_processes = num_processes or mp.cpu_count()
    
    def generate_batch(self, count, output_dir):
        """Generate batch using multiple processes"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Prepare work items
        work_items = []
        for i in range(count):
            seed = random.randint(0, 1000000)
            params = {'elements': random.randint(10, 50)}
            work_items.append((i, seed, params, output_dir))
        
        # Generate in parallel
        with mp.Pool(self.num_processes) as pool:
            results = pool.map(generate_single_worker, work_items)
        
        print(f"Generated {len(results)} artworks using {self.num_processes} processes")
        return results

# Usage
if __name__ == "__main__":
    generator = ParallelBatchGenerator()
    generator.generate_batch(100, "parallel_output")
```

## **Integration with vfab**

### **Automatic Queue Management**
```python
# auto_queue_manager.py
import subprocess
import time
from pathlib import Path

class AutoQueueManager:
    def __init__(self, max_queue_size=50):
        self.max_queue_size = max_queue_size
    
    def get_queue_size(self):
        """Get current vfab queue size"""
        result = subprocess.run(['vfab', 'list'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        return len(lines) - 1 if lines else 0  # Subtract header
    
    def add_to_queue(self, svg_file):
        """Add file to queue if space available"""
        if self.get_queue_size() < self.max_queue_size:
            subprocess.run(['vfab', 'add', svg_file])
            return True
        return False
    
    def monitor_and_add(self, source_dir):
        """Monitor directory and add files to queue"""
        source_path = Path(source_dir)
        
        for svg_file in sorted(source_path.glob("*.svg")):
            while not self.add_to_queue(str(svg_file)):
                print(f"Queue full, waiting... (current size: {self.get_queue_size()})")
                time.sleep(30)  # Wait 30 seconds
            
            print(f"Added {svg_file.name} to queue")

# Usage
if __name__ == "__main__":
    manager = AutoQueueManager(max_queue_size=30)
    manager.monitor_and_add("curated_output")
```

## **Batch Variations**

### **Theme-Based Generation**
```python
# themed_generator.py
class ThemedGenerator:
    def __init__(self):
        self.themes = {
            'nature': {
                'colors': [1, 2, 3],  # Green, brown, blue
                'shapes': ['organic', 'flowing'],
                'complexity': (0.3, 0.8)
            },
            'geometric': {
                'colors': [1, 4],  # Black, red
                'shapes': ['sharp', 'angular'],
                'complexity': (0.5, 1.0)
            },
            'minimal': {
                'colors': [1],  # Black only
                'shapes': ['simple', 'clean'],
                'complexity': (0.1, 0.4)
            }
        }
    
    def generate_themed_batch(self, theme, count):
        """Generate batch with specific theme"""
        theme_config = self.themes[theme]
        output_dir = f"themed_{theme}_output"
        Path(output_dir).mkdir(exist_ok=True)
        
        for i in range(count):
            vsk = vsketch.Vsketch()
            vsk.size("a4", center=True)
            
            # Apply theme constraints
            self.apply_theme(vsk, theme_config)
            
            filename = f"{theme}_{i:04d}.svg"
            vsk.save(f"{output_dir}/{filename}")
    
    def apply_theme(self, vsk, theme_config):
        """Apply theme to artwork"""
        # Implementation depends on your art style
        pass
```

## **Related Cheat Sheets**
- [vsketch Integration](vsketch-integration.md) - Core vsketch functionality
- [Design Optimization](design-optimization.md) - Optimize generated designs
- [Batch Production](../power-user/batch-production.md) - Professional batch workflows

## **Batch Generation Tips**
- **Start small**: Test with 5-10 artworks before scaling to hundreds
- **Monitor quality**: Use automated curation to maintain standards
- **Version control**: Keep generation scripts and metadata
- **Parallel processing**: Use multiple cores for faster generation
- **Queue management**: Don't overwhelm vfab with too many jobs at once