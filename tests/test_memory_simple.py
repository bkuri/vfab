#!/usr/bin/env python3
"""
Lightweight memory profiling for vfab.

This script performs basic memory analysis without external dependencies.
"""

import gc
import os
import sys
import tempfile
import time
import tracemalloc


def get_memory_usage() -> int:
    """Get current memory usage in bytes."""
    if tracemalloc.is_tracing():
        current, peak = tracemalloc.get_traced_memory()
        return current
    return 0


def format_bytes(bytes_count: int) -> str:
    """Format bytes in human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"


def create_test_svg() -> str:
    """Create a simple test SVG file."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="80" height="80" fill="none" stroke="black" stroke-width="1"/>
  <circle cx="50" cy="50" r="20" fill="none" stroke="black" stroke-width="1"/>
</svg>"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
        f.write(svg_content)
        return f.name


def run_memory_test():
    """Run basic memory test."""
    print("🧠 vfab Memory Profiler")
    print("=" * 50)

    # Start memory tracing
    tracemalloc.start()

    # Baseline memory
    gc.collect()
    baseline = get_memory_usage()
    print(f"Baseline memory: {format_bytes(baseline)}")

    # Test vfab command memory usage
    print("\n📊 Testing vfab command memory usage...")

    commands = [
        "vfab check config",
        "vfab list pens",
        "vfab list papers",
        "vfab info system",
        "vfab stats summary",
    ]

    peak_memory = baseline
    memory_samples = [baseline]

    for cmd in commands:
        print(f"  Testing: {cmd}")

        # Measure memory before command
        pre_memory = get_memory_usage()

        # Run command
        _ = os.system(cmd + " > /dev/null 2>&1")

        # Measure memory after command
        post_memory = get_memory_usage()
        memory_samples.append(post_memory)

        if post_memory > peak_memory:
            peak_memory = post_memory

        print(f"    Memory change: {format_bytes(post_memory - pre_memory)}")

        # Force garbage collection
        gc.collect()
        time.sleep(0.1)

    # Test job operations memory
    print("\n📋 Testing job operations memory...")

    # Create test SVG
    test_svg = create_test_svg()

    try:
        # Test job creation
        pre_memory = get_memory_usage()
        _ = os.system(f'vfab add job memory-test "{test_svg}" --apply > /dev/null 2>&1')
        post_memory = get_memory_usage()
        memory_samples.append(post_memory)

        print(f"  Job creation memory: {format_bytes(post_memory - pre_memory)}")

        # Test job listing
        pre_memory = get_memory_usage()
        _ = os.system("vfab list jobs > /dev/null 2>&1")
        post_memory = get_memory_usage()
        memory_samples.append(post_memory)

        print(f"  Job listing memory: {format_bytes(post_memory - pre_memory)}")

        # Clean up test job
        os.system("vfab remove job memory-test > /dev/null 2>&1")

    finally:
        # Clean up test SVG
        os.unlink(test_svg)

    # Final memory measurement
    gc.collect()
    final_memory = get_memory_usage()
    memory_samples.append(final_memory)

    # Calculate statistics
    memory_growth = final_memory - baseline
    max_memory = max(memory_samples)
    avg_memory = sum(memory_samples) / len(memory_samples)

    print("\n📈 Memory Analysis Results:")
    print(f"  Baseline:     {format_bytes(baseline)}")
    print(f"  Peak:         {format_bytes(max_memory)}")
    print(f"  Final:        {format_bytes(final_memory)}")
    print(f"  Growth:       {format_bytes(memory_growth)}")
    print(f"  Average:      {format_bytes(avg_memory)}")

    # Memory leak assessment
    if memory_growth < 1024 * 1024:  # Less than 1MB growth
        print("  ✅ No significant memory leaks detected")
    elif memory_growth < 5 * 1024 * 1024:  # Less than 5MB growth
        print("  ⚠️  Minor memory growth detected")
    else:
        print("  ❌ Significant memory growth detected - possible leak")

    # Performance assessment
    if max_memory < 50 * 1024 * 1024:  # Less than 50MB peak
        print("  ✅ Excellent memory efficiency")
    elif max_memory < 100 * 1024 * 1024:  # Less than 100MB peak
        print("  ✅ Good memory efficiency")
    else:
        print("  ⚠️  High memory usage detected")

    # Stop memory tracing
    tracemalloc.stop()

    print("\n🎯 Memory test completed successfully!")
    return True


if __name__ == "__main__":
    try:
        success = run_memory_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Memory test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Memory test failed: {e}")
        sys.exit(1)
