from ..system import get_cpu, get_disk, get_distro, get_kernel,\
    get_memory, get_processes, get_uptime, get_user


def get_system_data():
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
        "cpu": get_cpu(),
        "mem": get_memory(),
        "disk": get_disk(),
        "user": get_user(),
        "platform": {
            'distro': get_distro(),
            'kernel': get_kernel(),
            "uptime": get_uptime()
        },
        "processes": get_processes()
    }
