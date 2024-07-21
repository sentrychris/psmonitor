from psutil import cpu_count
from concurrent.futures import ThreadPoolExecutor

from ..system import get_cpu, get_disk, get_memory, get_processes, get_uptime


# Determine the number of available CPU cores
num_cores = cpu_count(logical=True)
max_workers = num_cores * 4

# Create a thread pool executor for parallel data gathering
executor = ThreadPoolExecutor(max_workers=max_workers)


def get_system_data():
    """
    Gathers system data including CPU, memory, disk usage, uptime, and processes.

    This function collects various system statistics and returns them in a dictionary.

    Returns:
        dict: A dictionary containing the following keys:
            - "cpu": CPU usage, temperature, and frequency.
            - "mem": Memory usage statistics.
            - "disk": Disk usage statistics.
            - "uptime": System uptime.
            - "processes": List of top 10 processes by memory usage.
    """

    futures = {
        "cpu": executor.submit(get_cpu),
        "mem": executor.submit(get_memory),
        "disk": executor.submit(get_disk),
        "uptime": executor.submit(get_uptime),
        "processes": executor.submit(get_processes)
    }

    return {key: future.result() for key, future in futures.items()}