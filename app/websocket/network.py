import asyncio
from psutil import cpu_count
from concurrent.futures import ThreadPoolExecutor

from ..network import get_avg_in_out, get_interfaces, get_statistics

# Determine the number of available CPU cores
num_cores = cpu_count(logical=True)
max_workers = num_cores * 4

# Create a thread pool executor for parallel data gathering
executor = ThreadPoolExecutor(max_workers=max_workers)


def get_network_data(avg_in_out=False):
    """
    Gathers network data including interface details and statistics.

    This function retrieves the list of network interfaces and their statistics. Optionally,
    it can also calculate the average network I/O statistics over a specified interval for each interface.

    Args:
        avg_in_out (bool): If True, calculates and includes average network I/O statistics over a specified interval.
                           Defaults to False.

    Returns:
        dict: A dictionary containing network interfaces, their statistics, and optionally their average I/O statistics.
              The structure is as follows:
                - "interfaces": List of network interface names.
                - "statistics": A dictionary of network statistics for each interface.
                - "averages" (optional): A dictionary of average network I/O statistics for each interface (included only if avg_in_out is True).
    """

    futures = {
        "interfaces": executor.submit(get_interfaces),
        "statistics": executor.submit(get_statistics),
    }

    if avg_in_out is True:
        interfaces = get_interfaces()

        averages = {}
        for interface in interfaces:
            averages[interface] = executor.submit(asyncio.run(get_avg_in_out(interface)))
        futures["averages"] = averages

    return {key: future.result() for key, future in futures.items()}
