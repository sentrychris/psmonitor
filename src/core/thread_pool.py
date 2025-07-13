import psutil
from concurrent.futures import ThreadPoolExecutor

# Determine the number of available CPU cores
num_cores = psutil.cpu_count(logical=True)

# Create a thread pool executor for parallel data gathering
executor = ThreadPoolExecutor(max_workers=min(num_cores * 2, 16))
