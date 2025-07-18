"""
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
"""

import os
import psutil
import platform
import sys
import subprocess
import functools
from collections import defaultdict


# Platform-specific imports
if sys.platform == "win32":
    import ctypes
    import getpass
elif sys.platform == 'linux':
    import pwd


# Determine if the script is running in a bundle created by PyInstaller
if getattr(sys, 'frozen', False):
    # The script is running in a bundled executable
    bundle_dir = sys._MEIPASS
else:
    # The script is running in a normal Python environment
    bundle_dir = os.path.abspath(os.path.join(os.getcwd(), 'bin'))


def convert_bytes(x: int, pre: int = 2) -> float:
    """
    Converts a size in bytes to gigabytes, rounded to a specified precision.

    Args:
        x (int): The size in bytes to be converted.
        pre (int, optional): The number of decimal places to round to. Defaults to 2.

    Returns:
        float: The size in gigabytes, rounded to the specified precision.
    """

    return round(x / (1024.0 ** 3), pre)


def get_cpu() -> dict:
    """
    Retrieves CPU usage statistics.

    This function collects CPU usage percentage, temperature, and frequency.

    Returns:
        dict: A dictionary containing the following keys:
            - "usage": CPU usage percentage.
            - "temp": CPU temperature (fixed value for now).
            - "freq": Current CPU frequency in MHz.
    """

    if sys.platform == "win32":
        executable_path = os.path.join(bundle_dir, 'libwincputemp.exe')
        proc = subprocess.check_output(
            executable_path,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        cpu_temp = proc.decode('utf-8').rstrip('\r\n') # TODO find an acceptable alternative for temps on windows.
    else:
        cpu_temp = round(psutil.sensors_temperatures()['coretemp'][0].current, 2)


    return {
        'usage': round(psutil.cpu_percent(), 2),
        'temp': cpu_temp,
        'freq': round(psutil.cpu_freq().current, 2)
    }


def get_disk() -> dict:
    """
    Retrieves disk usage statistics.

    This function collects total, used, and free disk space, as well as the disk usage percentage.

    Returns:
        dict: A dictionary containing the following keys:
            - "total": Total disk space in GB.
            - "used": Used disk space in GB.
            - "free": Free disk space in GB.
            - "percent": Disk usage percentage.
    """

    disk_data = psutil.disk_usage('/')

    return {
        'total': convert_bytes(disk_data.total),
        'used': convert_bytes(disk_data.used),
        'free': convert_bytes(disk_data.free),
        'percent': disk_data.percent,
    }


def get_memory() -> dict:
    """
    Retrieves memory usage statistics.

    This function collects total, used, and free memory, as well as the memory usage percentage.

    Returns:
        dict: A dictionary containing the following keys:
            - "total": Total memory in GB.
            - "used": Used memory in GB.
            - "free": Free memory in GB.
            - "percent": Memory usage percentage.
    """

    memory_data = psutil.virtual_memory()

    return {
        'total': convert_bytes(memory_data.total),
        'used': convert_bytes(memory_data.used),
        'free': convert_bytes(memory_data.free),
        'percent': memory_data.percent,
    }


def get_processes() -> list:
    """
    Retrieves a list of top 10 processes by memory usage.

    This function collects process information including PID, name, username, and memory usage,
    and returns the top 10 processes sorted by memory usage.

    Returns:
        list: A list of dictionaries, each containing the following keys:
            - "pid": Process ID.
            - "name": Process name.
            - "username": Username of the process owner.
            - "mem": Memory usage of the process in MB.
    """
    
    aggregated = defaultdict(lambda: {'mem': 0.0, 'pids': [], 'usernames': set()})

    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info']):
        try:
            info = proc.info
            mem_mb = info['memory_info'].rss / (1024 * 1024)
            name = info['name'] or 'unknown'
            aggregated[name]['mem'] += mem_mb
            aggregated[name]['pids'].append(info['pid'])
            if info['username']:
                aggregated[name]['usernames'].add(info['username'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    combined_list = []
    for name, data in aggregated.items():
        combined_list.append({
            'pid': data['pids'][0] if data['pids'] else '',
            'name': name,
            'username': ', '.join(data['usernames']) if data['usernames'] else '',
            'mem': round(data['mem'], 2)
        })

    return sorted(combined_list, key=lambda x: x['mem'], reverse=True)[:10]


def get_uptime() -> str:
    """
    Retrieves system uptime.

    This function reads the system uptime from the '/proc/uptime' file and formats
    it into a human-readable string.

    Returns:
        str: A string representing the system uptime in days, hours, minutes, and seconds.
            If the file cannot be read, returns an error message.
    """

    if sys.platform == "win32":
        try:
            uptime_ms = ctypes.windll.kernel32.GetTickCount64()
            total_seconds = uptime_ms / 1000.0
        except Exception:
            return "N/A"
    else:
        try:
            with open('/proc/uptime') as f:
                total_seconds = float(f.read().split()[0])
        except Exception:
            return "N/A"

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    uptime_parts = [
        f"{int(days)} day{'s' if days != 1 else ''}" if days else "",
        f"{int(hours)} hr{'s' if hours != 1 else ''}" if hours else "",
        f"{int(minutes)} min{'s' if minutes != 1 else ''}" if minutes else "",
        f"{int(seconds)} sec{'s' if seconds != 1 else ''}" if seconds else ""
    ]

    return ", ".join(part for part in uptime_parts if part)


@functools.lru_cache(maxsize=1024)
def get_user() -> str:
    """
    Retrieves the username of the current user.

    On Windows, it uses the `getpass.getuser()` function.
    On Unix-like systems, it uses the `pwd` module to get the username associated with the current process's user ID.

    Returns:
        str: The username of the current user.
    """

    if sys.platform == "win32":
        return getpass.getuser()
    else:
        return pwd.getpwuid(os.getuid())[0]


@functools.lru_cache(maxsize=1024)
def get_distro() -> str:
    """
    Retrieves the name of the operating system distribution.

    On Windows, it uses the `wmic` command to get the OS caption.
    On Unix-like systems, it reads the `/etc/*-release` file to get the distribution name.

    Returns:
        str: The name of the operating system distribution.
    """

    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.check_output(['wmic', 'os', 'get', 'Caption'], text=True, startupinfo=startupinfo)
        os_name = result.strip().split('\n')

        return os_name[2].strip() if len(os_name) > 1 else "Unknown OS"
    else:
        return os.popen('cat /etc/*-release | grep "^PRETTY_NAME=" | cut -d= -f2').read().replace('"', '').strip()


@functools.lru_cache(maxsize=1024)
def get_kernel() -> str:
    """
    Retrieves the kernel version of the operating system.

    On Windows, it uses `platform.version()` to get the version of the OS.
    On Unix-like systems, it uses `platform.release()` to get the kernel version.

    Returns:
        str: The kernel version of the operating system.
    """

    if sys.platform == "win32":
        return platform.version()
    else:
        return platform.release()
