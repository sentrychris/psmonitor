import psutil


def data():
    system = dict()
    system["cpu"] = cpu()
    system["memory"] = memory()
    system["uptime"] = uptime()

    return str(system["cpu"]["temp"])


def uptime():
    try:
        f = open("/proc/uptime")
        contents = f.read().split()
        f.close()
    except Exception:
        return "Cannot open uptime file: /proc/uptime"

    return float(contents[0])


def cpu():
    return {
        'usage': round(psutil.cpu_percent(1), 2),
        'temp': 50,  # round(psutil.sensors_temperatures()['cpu_thermal'][0].current, 2),
        'freq': round(psutil.cpu_freq().current, 2)
    }


def memory():
    mem = psutil.virtual_memory()

    return {
        'total': round(mem.total / (1024.0 ** 3), 2),
        'used': round(mem.used / (1024.0 ** 3), 2),
        'free': round(mem.free / (1024.0 ** 3), 2),
        'percent': mem.percent
    }
