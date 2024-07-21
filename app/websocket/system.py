import asyncio

from ..thread_pool import executor
from ..system import get_cpu, get_disk, get_memory, get_processes, get_uptime


async def get_system_data():
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

    loop = asyncio.get_running_loop()

    futures = {
        "cpu": loop.run_in_executor(executor, get_cpu),
        "mem": loop.run_in_executor(executor, get_memory),
        "disk": loop.run_in_executor(executor, get_disk),
        "uptime": loop.run_in_executor(executor, get_uptime),
        "processes": loop.run_in_executor(executor, get_processes),
    }

    results = {key: await future for key, future in futures.items()}

    return results