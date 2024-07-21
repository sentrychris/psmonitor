import netifaces
import re
import subprocess


def parse_wifi_info():
    cells = [[]]
    info = {}

    interface = get_wifi_interface()
    print(interface)

    try:
        interface = get_wifi_interface()
        print(str(" interface: ") + interface)
        proc = subprocess.Popen(["iwlist", interface, "scan"], stdout=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()

        for line in out.split("\n"):
            cell_line = match(line, "Cell ")
            if cell_line is not None:
                cells.append([])
                line = cell_line[-27:]
            cells[-1].append(line.rstrip())

        cells = cells[1:]

        for cell in cells:
            info.update(parse_cell(cell))
    except Exception:
        pass

    return info


def get_wifi_interface():
    interfaces = netifaces.interfaces()
    print(interfaces)


def run_wifi_speedtest():
    speedtest = subprocess.Popen('speedtest-cli --simple', shell=True,
                                 stdout=subprocess.PIPE).stdout.read().decode('utf-8')

    ping = re.findall(r'Ping:\s(.*?)\s', speedtest, re.MULTILINE)
    download = re.findall(r'Download:\s(.*?)\s', speedtest, re.MULTILINE)
    upload = re.findall(r'Upload:\s(.*?)\s', speedtest, re.MULTILINE)

    response = {}
    try:
        response.update({
            'ping': ping[0].replace(',', '.'),
            'download': download[0].replace(',', '.'),
            'upload': upload[0].replace(',', '.')
        })
    except Exception:
        pass

    return response


def get_name(cell):
    return matching_line(cell, "ESSID:")[1:-1]


def get_quality(cell):
    quality = matching_line(cell, "Quality=").split()[0].split('/')
    return str(int(round(float(quality[0]) / float(quality[1]) * 100))).rjust(3)


def get_channel(cell):
    return matching_line(cell, "Channel:")


def get_signal_level(cell):
    return matching_line(cell, "Quality=").split("Signal level=")[1]


def get_encryption(cell):
    enc = ""
    if matching_line(cell, "Encryption key:") == "off":
        enc = "Open"
    else:
        for line in cell:
            matching = match(line, "IE:")
            if matching is not None:
                wpa = match(matching, "WPA Version ")
                if wpa is not None:
                    enc = "WPA v." + wpa
        if enc == "":
            enc = "WEP"
    return enc


def get_address(cell):
    return matching_line(cell, "Address: ")


def matching_line(lines, keyword):
    for line in lines:
        matching = match(line, keyword)
        if matching is not None:
            return matching
    return None


def match(line, keyword):
    line = line.lstrip()
    length = len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        return


def parse_cell(cell):
    rules = {
        "name": get_name,
        "quality": get_quality,
        "channel": get_channel,
        "encryption": get_encryption,
        "address": get_address,
        "signal": get_signal_level
    }

    parsed_cell = {}
    for key in rules:
        rule = rules[key]
        parsed_cell.update({key: rule(cell)})

    return parsed_cell

print(parse_wifi_info())