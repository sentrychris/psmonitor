import ctypes
import getpass
import os
import psutil
import platform
import sys


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
        cpu_temp = "N/A" # TODO find an acceptable alternative for temps on windows.
    else:
        cpu_temp = round(psutil.sensors_temperatures()['coretemp'][0].current, 2)


    return {
        'usage': round(psutil.cpu_percent(1), 2),
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
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info']):
        try:
            process_info = proc.info
            process_info['mem'] = round(process_info['memory_info'].rss / (1024 * 1024), 2)
            processes.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return sorted(processes, key=lambda p: p['mem'], reverse=True)[:10]


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
        import pwd
        return pwd.getpwuid(os.getuid())[0]


def get_distro() -> str:
    """
    Retrieves the name of the operating system distribution.

    On Windows, it uses the `wmic` command to get the OS caption.
    On Unix-like systems, it reads the `/etc/*-release` file to get the distribution name.

    Returns:
        str: The name of the operating system distribution.
    """

    if sys.platform == "win32":
        import subprocess
        result = subprocess.run(['wmic', 'os', 'get', 'Caption'], capture_output=True, text=True, check=True)
        os_name = result.stdout.strip().split('\n')
        return os_name[2].strip() if len(os_name) > 1 else "Unknown OS"
    else:
        return os.popen('cat /etc/*-release | grep "^PRETTY_NAME=" | cut -d= -f2').read().replace('"', '').strip()


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
