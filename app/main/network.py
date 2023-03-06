import psutil
from asyncio import sleep


async def network_data():
    network = dict()
    network["stats"] = await stats()


async def stats(inet="wlan0"):
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inet]
    net_in_1 = net_stat.bytes_recv
    net_out_1 = net_stat.bytes_sent

    await sleep(1)

    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inet]
    net_in_2 = net_stat.bytes_recv
    net_out_2 = net_stat.bytes_sent

    net_in = round((net_in_2 - net_in_1) / 1024 / 1024, 3)
    net_out = round((net_out_2 - net_out_1) / 1024 / 1024, 3)

    return dict({
        "interface": inet,
        "in": net_in,
        "out": net_out
    })