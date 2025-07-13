from tornado.ioloop import IOLoop
from ...thread_pool import executor
from ...service.system_service import get_cpu, get_disk, get_memory, get_processes, get_uptime


async def get_system_data() -> dict:
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

    loop = IOLoop.current()

    tasks = {
        key: loop.run_in_executor(executor, fn)
        for key, fn in {
            "cpu": get_cpu,
            "mem": get_memory,
            "disk": get_disk,
            "uptime": get_uptime,
            "processes": get_processes,
        }.items()
    }

    results = {key: await task for key, task in tasks.items()}

    return results