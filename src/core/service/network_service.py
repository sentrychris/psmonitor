"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: network_service.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import asyncio
import psutil


async def get_avg_in_out(nic="wlan0", interval=5) -> dict:
    """
    Calculates average network statistics for a given network interface over a
    specified interval.

    Args:
        nic (str): The network interface controller to monitor (default is "wlan0").
        interval (int): The duration in seconds over which to measure.

    Returns:
        dict: A dictionary containing the following network statistics:
            - "interface": The network interface being measured.
            - "in": Average amount of data received in MB per second.
            - "out": Average amount of data sent in MB per second.
    """

    stat_1 = psutil.net_io_counters(pernic=True, nowrap=True)[nic]
    in_1, out_1 = stat_1.bytes_recv, stat_1.bytes_sent

    await asyncio.sleep(interval)

    stat_2 = psutil.net_io_counters(pernic=True, nowrap=True)[nic]
    in_2, out_2 = stat_2.bytes_recv, stat_2.bytes_sent

    avg_in = round((in_2 - in_1) / interval / 1024 / 1024, 3)
    avg_out = round((out_2 - out_1) / interval / 1024 / 1024, 3)

    return {
        "interface": nic,
        "in": avg_in,
        "out": avg_out
    }


def get_statistics() -> dict:
    """
    Retrieves network statistics for all network interfaces on the system.

    This function uses the `psutil` library to gather network I/O statistics for each
    network interface and returns these statistics in a structured format.

    Returns:
        dict: A dictionary where each key is a network interface name, and the value is
            another dictionary containing the following network statistics:
                - "mb_sent": Amount of data sent in megabytes.
                - "mb_received": Amount of data received in megabytes.
                - "pk_sent": Number of packets sent.
                - "pk_received": Number of packets received.
                - "error_in": Number of input errors.
                - "error_out": Number of output errors.
                - "dropout": Number of packets dropped.
    """

    interfaces = {}
    for addr, stat in psutil.net_io_counters(pernic=True).items():
        interfaces[addr] = {
            "mb_sent": stat.bytes_sent / (1024.0 * 1024.0),
            "mb_received": stat.bytes_recv / (1024.0 * 1024.0),
            "pk_sent": stat.packets_sent,
            "pk_received": stat.packets_recv,
            "error_in": stat.errin,
            "error_out": stat.errout,
            "dropout": stat.dropout,
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
