from psutil import cpu_count
from concurrent.futures import ThreadPoolExecutor

# Determine the number of available CPU cores
num_cores = cpu_count(logical=True)
max_workers = num_cores * 4

# Create a thread pool executor for parallel data gathering
executor = ThreadPoolExecutor(max_workers=max_workers)
