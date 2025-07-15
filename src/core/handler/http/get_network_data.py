from ...service.network_service import get_avg_in_out, get_interfaces, get_statistics
from ...service.wifi_service import get_wifi_data


async def get_network_data(avg_in_out=False) -> dict:
    """
    Gathers network data including interface details and statistics.

    This function retrieves the list of network interfaces and their statistics. Optionally,
    it can also calculate the average network I/O statistics over a specified interval for each interface.

    Args:
        avg_in_out (bool): If True, calculates and includes average network I/O statistics over a specified interval.
                           Defaults to False.

    Returns:
        dict: A dictionary containing network interfaces, their statistics, and optionally their average I/O statistics.
              The structure is as follows:
                - "interfaces": List of network interface names.
                - "statistics": A dictionary of network statistics for each interface.
                - "averages" (optional): A dictionary of average network I/O statistics for each interface (included only if avg_in_out is True).
    """

    results = {
        "interfaces": get_interfaces(),
        "wireless": get_wifi_data(),
        "statistics": get_statistics(),
    }

    if avg_in_out:
        interfaces = results["interfaces"]
        averages = {
            "interface": await get_avg_in_out(interface) for interface in interfaces
        }
        results["averages"] = averages

    return results
