import psutil
from concurrent.futures import ThreadPoolExecutor

# Determine the number of available CPU cores
num_cores = psutil.cpu_count(logical=True)

def get_max_workers() -> int:
    """
    Determines the maximum number of worker threads based on CPU load.

    The function checks the current CPU load over a 1-second interval.
    If the CPU load is less than 50%, it returns `num_cores * 8`.
    If the CPU load is 50% or higher, it returns `num_cores * 4`.

    Returns:
        int: The maximum number of worker threads.
    """

    load = psutil.cpu_percent(interval=1)
    if load < 50:
        return num_cores * 8
    else:
        return num_cores * 4

# Create a thread pool executor for parallel data gathering
max_workers = get_max_workers()
executor = ThreadPoolExecutor(max_workers=max_workers)
