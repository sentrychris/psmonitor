import re
import subprocess


def get_wifi_data():
    """
    Parses Wi-Fi information by scanning available Wi-Fi networks using the iwlist command.

    Returns:
        dict: A dictionary containing parsed Wi-Fi information.
    """

    cells = [[]]
    info = {}

    try:
        interface = get_wifi_interface()
        print(interface)
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
    """
    Gets the wi-fi interface using the iw command.

    Returns:
        str: the name of the wi-fi interface.
    """

    proc = subprocess.Popen(['iw', 'dev'], stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()

    interface = 'wlan0'
    for line in out.split("\n"):
        addr = match(line, "Interface ")
        if addr is not None:
            interface = addr

    return interface


def run_wifi_speedtest():
    """
    Runs a wi-fi speed test using speedtes-cli and parses the results.

    Returns:
        dict: A dictionary containing ping, download, and upload speeds.
    """

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
    """
    Extracts the ESSID (name) from a cell.

    Args:
        cell (list): the cell information.

    Returns:
        str: The ESSID.
    """

    return matching_line(cell, "ESSID:")[1:-1]


def get_quality(cell):
    """
    Extracts the quality from a cell and converts it to a percentage.

    Args:
        cell (list): the cell information.

    Returns:
        str: The quality of the cell as a percentage.
    """

    quality = matching_line(cell, "Quality=").split()[0].split('/')
    return str(int(round(float(quality[0]) / float(quality[1]) * 100))).rjust(3)


def get_channel(cell):
    """
    Extracts the channel from a cell.

    Args:
        cell (list): the cell information.

    Returns:
        str: The wi-fi channel.
    """

    return matching_line(cell, "Channel:")


def get_signal_level(cell):
    """
    Extracts the signal level from a cell.

    Args:
        cell (list): The cell information.

    Returns:
        str: The signal level of the cell.
    """

    return matching_line(cell, "Quality=").split("Signal level=")[1]


def get_encryption(cell):
    """
    Extracts the encryption type from a cell.

    Args:
        cell (list): The cell information.

    Returns:
        str: The encryption type of the cell.
    """

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
    """
    Extracts the address from a cell.

    Args:
        cell (list): The cell information.

    Returns:
        str: The address of the cell.
    """

    return matching_line(cell, "Address: ")


def matching_line(lines, keyword):
    """
    Finds the first line that matches a given keyword.

    Args:
        lines (list): The lines to search through.
        keyword (str): The keyword to search for.

    Returns:
        str: The matching line, or None if no match is found.
    """

    for line in lines:
        matching = match(line, keyword)
        if matching is not None:
            return matching
    return None


def match(line, keyword):
    """
    Checks if a line starts with a given keyword.

    Args:
        line (str): The line to check.
        keyword (str): The keyword to check for.

    Returns:
        str: The line with the keyword stripped, or None if no match.
    """

    line = line.lstrip()
    length = len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        return


def parse_cell(cell):
    """
    Parses a cell's information into a dictionary.

    Args:
        cell (list): The cell information.

    Returns:
        dict: A dictionary containing parsed cell information.
    """

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