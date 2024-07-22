import psutil
from concurrent.futures import ThreadPoolExecutor

# Determine the number of available CPU cores
num_cores = psutil.cpu_count(logical=True)

def get_max_workers():
    load = psutil.cpu_percent(interval=1)
    if load < 50:
        return num_cores * 8
    else:
        return num_cores * 4

# Create a thread pool executor for parallel data gathering
max_workers = get_max_workers()
executor = ThreadPoolExecutor(max_workers=max_workers)
