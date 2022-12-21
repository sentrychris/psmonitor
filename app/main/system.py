import psutil


def system_data():
    system = dict()
    system["cpu"] = cpu()
    system["mem"] = memory()
    system["uptime"] = uptime()

    return system


def uptime():
    try:
        f = open("/proc/uptime")
        contents = f.read().split()
        f.close()
    except Exception:
        return "Cannot open uptime file: /proc/uptime"

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
    return dict({
        'usage': round(psutil.cpu_percent(1), 2),
        'temp': round(psutil.sensors_temperatures()['cpu_thermal'][0].current, 2),
        'freq': round(psutil.cpu_freq().current, 2)
    })


def memory():
    mem = psutil.virtual_memory()

    return {
        'total': round(mem.total / (1024.0 ** 3), 2),
        'used': round(mem.used / (1024.0 ** 3), 2),
        'free': round(mem.free / (1024.0 ** 3), 2),
        'percent': mem.percent
    }
