#!/usr/bin/env python3
"""
Advanced memory profiling for ploTTY.

This script performs comprehensive memory analysis including:
- Baseline memory measurement
- Memory usage during job operations
- Memory leak detection
- Memory growth patterns
- Peak memory usage tracking
"""

import gc
import os
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from plotty.config import load_config
    from plotty.db import init_db, get_db
    from plotty.models import Job
except ImportError as e:
    print(f"Error importing ploTTY modules: {e}")
    print("Make sure you're running this from the ploTTY root directory")
    sys.exit(1)


if __name__ == "__main__":
    main()