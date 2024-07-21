import psutil

from asyncio import sleep


async def network_data():
    """
    Asynchronously gathers network data and returns network statistics.

    This function initializes a dictionary to store network statistics and
    calls the `stats` function to populate it with data for a specified network interface.

    Returns:
        dict: A dictionary containing network statistics for a specified network interface.
    """

    return {
        "stats": await get_statistics()
    }


async def get_statistics(inet="wlan0"):
    """
    Asynchronously calculates network statistics for a given network interface.

    This function calculates the amount of data sent and received over a specified network
    interface within a one-second interval.

    Args:
        inet (str): The network interface to monitor (default is "wlan0").

    Returns:
        dict: A dictionary containing the following network statistics:
            - "interface": The network interface being monitored.
            - "in": Amount of data received in MB over the interval.
            - "out": Amount of data sent in MB over the interval.
    """

    # Capture initial network stats
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inet]
    net_in_1 = net_stat.bytes_recv
    net_out_1 = net_stat.bytes_sent

    # Wait for a second to capture the delta
    await sleep(1)

    # Capture network stats after 1 second
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inet]
    net_in_2 = net_stat.bytes_recv
    net_out_2 = net_stat.bytes_sent

    # Calculate the data received and sent in MB
    net_in = round((net_in_2 - net_in_1) / 1024 / 1024, 3)
    net_out = round((net_out_2 - net_out_1) / 1024 / 1024, 3)

    return {
        "interface": inet,
        "in": net_in,
        "out": net_out
    }