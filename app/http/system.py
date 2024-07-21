import os
import pwd
import platform

from ..system import get_cpu, get_disk, get_memory, get_processes, get_uptime


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

    distro = os.popen('cat /etc/*-release | awk NR==1 | cut -c 12-').read().replace('"', '').rstrip()

    return {
        "cpu": get_cpu(),
        "mem": get_memory(),
        "disk": get_disk(),
        "user": get_user(),
        "platform": {
            'distro': distro,
            'kernel': platform.release(),
            "uptime": get_uptime()
        },
        "processes": get_processes()
    }


def get_user():
    return pwd.getpwuid(os.getuid())[0]
