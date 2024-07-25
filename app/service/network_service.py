import asyncio
import psutil


async def get_avg_in_out(inet="wlan0", interval=5, sample_rate=0.1) -> dict:
    """
    Asynchronously calculates average network statistics for a given network interface over a specified interval.

    Args:
        inet (str): The network interface to monitor (default is "wlan0").
        interval (int): The duration in seconds over which to average the network statistics.
        sample_rate (float): The sampling rate in seconds.

    Returns:
        dict: A dictionary containing the following network statistics:
            - "interface": The network interface being monitored.
            - "in": Average amount of data received in MB per second.
            - "out": Average amount of data sent in MB per second.
    """

    samples = int(interval / sample_rate)
    total_net_in = 0
    total_net_out = 0

    for _ in range(samples):
        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inet]
        net_in_1 = net_stat.bytes_recv
        net_out_1 = net_stat.bytes_sent

        await asyncio.sleep(sample_rate)

        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inet]
        net_in_2 = net_stat.bytes_recv
        net_out_2 = net_stat.bytes_sent

        total_net_in += (net_in_2 - net_in_1)
        total_net_out += (net_out_2 - net_out_1)

    avg_net_in = round((total_net_in / interval) / 1024 / 1024, 3)
    avg_net_out = round((total_net_out / interval) / 1024 / 1024, 3)

    return {
        "interface": inet,
        "in": avg_net_in,
        "out": avg_net_out
    }


def get_statistics() -> dict:
    """
    Retrieves network statistics for all network interfaces on the system.

    This function uses the `psutil` library to gather network I/O statistics for each
    network interface and returns these statistics in a structured format.

    Returns:
        dict: A dictionary where each key is a network interface name, and the value is
              another dictionary containing the following network statistics:
                - 'mb_sent': Amount of data sent in megabytes.
                - 'mb_received': Amount of data received in megabytes.
                - 'pk_sent': Number of packets sent.
                - 'pk_received': Number of packets received.
                - 'error_in': Number of input errors.
                - 'error_out': Number of output errors.
                - 'dropout': Number of packets dropped.
    """

    interfaces = {}
    for addr, stat in psutil.net_io_counters(pernic=True).items():
        interfaces[addr] = {
            'mb_sent': stat.bytes_sent / (1024.0 * 1024.0),
            'mb_received': stat.bytes_recv / (1024.0 * 1024.0),
            'pk_sent': stat.packets_sent,
            'pk_received': stat.packets_recv,
            'error_in': stat.errin,
            'error_out': stat.errout,
            'dropout': stat.dropout,
        }

    return interfaces


def get_interfaces() -> list:
    """
    Retrieves a list of network interface names on the system.

    This function uses the `psutil` library to get network interface addresses and returns
    the names of all network interfaces.

    Returns:
        list: A list of network interface names.

    Example:
        ["eth0", "wlan0", "lo"]
    """

    interfaces = psutil.net_if_addrs()

    return [*interfaces.keys()]
