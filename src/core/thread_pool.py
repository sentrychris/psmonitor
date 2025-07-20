"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: thread_pool.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.5.0.2413
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
from concurrent.futures import ThreadPoolExecutor

# Third-party imports
import psutil

# Determine the number of available CPU cores
num_cores = psutil.cpu_count(logical=True)

# Create a thread pool executor for parallel data gathering
executor = ThreadPoolExecutor(max_workers=min(num_cores * 2, 16))
