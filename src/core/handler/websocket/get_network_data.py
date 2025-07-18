"""
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
"""

# Third-party imports
from tornado.ioloop import IOLoop

# Local application imports
from core.thread_pool import executor
from core.service.network_service import get_avg_in_out, get_interfaces, get_statistics


async def get_network_data(avg_in_out=False) -> dict:
    """
    Gathers network data including interface details and statistics.

    This function retrieves the list of network interfaces and their statistics. Optionally,
    it can also calculate the average network I/O statistics over a specified interval for
    each interface.

    Args:
        avg_in_out (bool): If True, calculates and includes average network I/O statistics over
                           a specified interval. Defaults to False.

    Returns:
        dict: A dictionary containing network interfaces, their statistics, and optionally their
              average I/O statistics.

              The structure is as follows:
                - "interfaces": List of network interface names.
                - "statistics": A dictionary of network statistics for each interface.
                - "averages" (optional): A dictionary of average network I/O statistics for each
                                         interface (included only if avg_in_out is True).
    """

    loop = IOLoop.current()

    futures = {
        "interfaces": loop.run_in_executor(executor, get_interfaces),
        "statistics": loop.run_in_executor(executor, get_statistics),
    }

    results = {key: await future for key, future in futures.items()}

    if avg_in_out:
        interfaces = results["interfaces"]
        avg_futures = {
            interface: loop.run_in_executor(
                executor,
                get_avg_in_out,
                interface
            ) for interface in interfaces
        }
        results["averages"] = {interface: await future for interface, future in avg_futures.items()}

    return results
