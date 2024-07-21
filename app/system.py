import psutil


def system_data():
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

    system = dict()
    system["cpu"] = cpu()
    system["mem"] = memory()
    system["disk"] = disk()
    system["uptime"] = uptime()
    system["processes"] = processes()

    return system


def uptime():
    """
    Retrieves system uptime.

    This function reads the system uptime from the '/proc/uptime' file and formats
    it into a human-readable string.

    Returns:
        str: A string representing the system uptime in days, hours, minutes, and seconds.
              If the file cannot be read, returns an error message.
    """

    try:
        f = open('/proc/uptime')
        contents = f.read().split()
        f.close()
    except Exception:
        return 'Cannot open uptime file: /proc/uptime'

    total_seconds = float(contents[0])
    days = int(total_seconds / 86400)
    hours = int((total_seconds % 86400) / 3600)
    minutes = int((total_seconds % 3600) / 60)
    seconds = int(total_seconds % 60)

    uptime = ""

    if days > 0:
        uptime += str(days) + " " + (days == 1 and "day" or "days") + ", "
    if len(uptime) > 0 or hours > 0:
        uptime += str(hours) + " " + (hours == 1 and "hour" or "hours") + ", "
    if len(uptime) > 0 or minutes > 0:
        uptime += str(minutes) + " " + (minutes == 1 and "minute" or "minutes") + ", "

    uptime += str(seconds) + " " + (seconds == 1 and "second" or "seconds")

    return uptime


def cpu():
    """
    Retrieves CPU usage statistics.

    This function collects CPU usage percentage, temperature, and frequency.

    Returns:
        dict: A dictionary containing the following keys:
            - "usage": CPU usage percentage.
            - "temp": CPU temperature (fixed value for now).
            - "freq": Current CPU frequency in MHz.
    """

    return dict({
        'usage': round(psutil.cpu_percent(1), 2),
        'temp': 50,  # Placeholder value for CPU temperature
        'freq': round(psutil.cpu_freq().current, 2)
    })


def memory():
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

    mem = psutil.virtual_memory()

    return dict({
        'total': round(mem.total / (1024.0 ** 3), 2),
        'used': round(mem.used / (1024.0 ** 3), 2),
        'free': round(mem.free / (1024.0 ** 3), 2),
        'percent': mem.percent
    })


def disk():
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

    disk = psutil.disk_usage('/')

    return dict({
        'total': round(disk.total / (1024.0 ** 3), 2),
        'used': round(disk.used / (1024.0 ** 3), 2),
        'free': round(disk.free / (1024.0 ** 3), 2),
        'percent': disk.percent
    })


def processes():
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
    for proc in psutil.process_iter():
        try:
            process = proc.as_dict(attrs=['pid', 'name', 'username'])
            process['mem'] = round(proc.memory_info().rss / (1024 * 1024), 2)
            processes.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    processes = sorted(processes, key=lambda sort: sort['mem'], reverse=True)

    return processes[:10]
