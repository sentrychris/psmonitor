"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: get_system_data.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 2.0.0.1011
License: MIT
--------------------------------------------------------------------------
"""

# Local application imports
import core.service.system_service as psm


def get_system_data() -> dict:
    """
    Gathers system data including CPU, memory, disk usage, uptime, and processes.

    This function collects various system statistics and returns them in a dictionary.

    Returns:
        dict: A dictionary containing the following keys:
            - "cpu": CPU usage, temperature, and frequency.
            - "mem": Memory usage statistics.
            - "disk": Disk usage statistics.
            - "user": Logged in user.
            - "platform": Distribution, kernel version and uptime.
            - "processes": List of top 10 processes by memory usage.
    """

    return {
        "cpu": psm.get_cpu(),
        "mem": psm.get_memory(),
        "disk": psm.get_disk(),
        "user": psm.get_user(),
        "platform": {
            "distro": psm.get_distro(),
            "kernel": psm.get_kernel(),
            "uptime": psm.get_uptime()
        },
        "processes": psm.get_processes()
    }
