import uuid
import json
import os.path
import signal
import platform
import requests
import websocket
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from app import create_app, signal_handler


# Constants
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(BASE_DIR, 'public')
STATIC_PATH = os.path.join(BASE_DIR, 'public')
COOKIE_SECRET = uuid.uuid1().hex
WS_URL = 'ws://localhost:4500/connect?id='
HTTP_URL = 'http://localhost:4500'


# Data structure
data = {
    "cpu": {"usage": 0.0, "temp": 0, "freq": 0},
    "mem": {"total": 0, "used": 0, "free": 0, "percent": 0},
    "disk": {"total": 0, "used": 0, "free": 0, "percent": 0},
    "user": "",
    "platform": {"distro": "", "kernel": "", "uptime": ""},
    "uptime": "",
    "processes": []
}


def start_server():
    app = create_app({
        'template_path': TEMPLATE_PATH,
        'static_path': STATIC_PATH,
        'cookie_secret': COOKIE_SECRET,
        'xsrf_cookies': False,
        'debug': True
    })

    http = HTTPServer(app)
    http.listen(port=4500, address='localhost')
    print("Listening on http://localhost:4500")
    IOLoop.current().start()


class SystemMonitorApp(tk.Tk):

    def __init__(self, data):
        super().__init__()
        self.title("PSMonitor - System monitoring utility")
        self.geometry("460x480")
        self.resizable(False, False)
        self.image_cache = {}

        app_icon = os.path.join(BASE_DIR, 'public', 'assets', 'icons', 'psmonitor.png')
        self.set_window_icon(app_icon)
        self.create_widgets(data)
        self.ws = None
        self.ws_thread = None

        self.fetch_initial_data()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def set_window_icon(self, icon_path):
        icon = Image.open(icon_path)
        icon = icon.resize((32, 32), Image.LANCZOS)
        icon_photo = ImageTk.PhotoImage(icon)
        self.iconphoto(True, icon_photo)


    def create_widgets(self, data):
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=5, pady=5)

        self.platform_frame = self.create_section_frame(main_frame, "Platform")
        self.add_label_with_icon(self.platform_frame, "", data['platform']['distro'])
        self.add_label(self.platform_frame, "Kernel:", data['platform']['kernel'])
        self.add_label(self.platform_frame, "Up:", data['platform']['uptime'])
        self.platform_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.disk_frame = self.create_section_frame(main_frame, "Disk")
        self.add_label(self.disk_frame, "Used:", f"{data['disk']['used']} GB")
        self.add_label(self.disk_frame, "Free:", f"{data['disk']['free']} GB")
        self.add_label(self.disk_frame, "Usage:", f"{data['disk']['percent']} %")
        self.disk_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.cpu_frame = self.create_section_frame(main_frame, "CPU")
        self.add_label(self.cpu_frame, "Temperature:", f"{data['cpu']['temp']} °C")
        self.add_label(self.cpu_frame, "Frequency:", f"{data['cpu']['freq']} MHz")
        self.add_label(self.cpu_frame, "Usage:", f"{data['cpu']['usage']} %")
        self.cpu_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.mem_frame = self.create_section_frame(main_frame, "Memory")
        self.add_label(self.mem_frame, "Used:", f"{data['mem']['used']} GB")
        self.add_label(self.mem_frame, "Free:", f"{data['mem']['free']} GB")
        self.add_label(self.mem_frame, "Usage:", f"{data['mem']['percent']} %")
        self.mem_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        self.processes_frame = self.create_section_frame(main_frame, "Top Processes")
        self.add_processes_table(self.processes_frame, data['processes'])
        self.processes_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)


    def create_section_frame(self, parent, title):
        section_frame = ttk.LabelFrame(parent, text=title)
        section_frame.grid(sticky="nsew", padx=5, pady=5)
        return section_frame


    def add_label(self, frame, text, value):
        label = ttk.Label(frame, text=f"{text} {value}")
        label.grid(sticky='w', padx=5, pady=2)


    def load_image(self, path, width):
        if path in self.image_cache:
            return self.image_cache[path]
        image = Image.open(path)
        image = image.resize((width, int(image.height * width / image.width)), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image_cache[path] = photo
        return photo


    def add_label_with_icon(self, frame, text, value):
        container = ttk.Frame(frame)
        container.grid(sticky='w', padx=5, pady=2)
        icon_file = 'windows.png'
        icon_width = 14
        if platform.system() == 'Darwin':
            icon_file = 'macOS.png'
            icon_width = 16
        elif platform.system() == 'Linux':
            icon_width = 18
            icon_file = 'linux.png'
        png_path = os.path.join(BASE_DIR, 'public', 'assets', 'icons', icon_file)
        photo = self.load_image(png_path, icon_width)
        icon_label = ttk.Label(container, image=photo)
        icon_label.image = photo
        icon_label.pack(side=tk.LEFT)
        text_label = ttk.Label(container, text=f"{text} {value}")
        text_label.pack(side=tk.LEFT)


    def add_processes_table(self, frame, processes_data):
        columns = ("pid", "name", "username", "mem")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        self.tree.heading("pid", text="PID", anchor='center')
        self.tree.column("pid", anchor='center', width=60, minwidth=50)
        self.tree.heading("name", text="Name", anchor='center')
        self.tree.column("name", anchor='center', width=100, minwidth=80)
        self.tree.heading("username", text="Username", anchor='center')
        self.tree.column("username", anchor='center', width=120, minwidth=100)
        self.tree.heading("mem", text="Memory (MB)", anchor='center')
        self.tree.column("mem", anchor='center', width=80, minwidth=60)
        for i, process in enumerate(processes_data):
            values = (process['pid'], process['name'], process['username'], process['mem'])
            tag = "odd" if i % 2 == 0 else "even"
            self.tree.insert("", "end", values=values, tags=(tag,))
        self.tree.tag_configure("odd", background="lightgrey")
        self.tree.tag_configure("even", background="white")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)


    def fetch_initial_data(self):
        try:
            response = requests.get(f'{HTTP_URL}/system')
            initial_data = response.json()
            self.update_initial_data(initial_data)
            self.start_websocket_connection()
        except requests.RequestException as e:
            print(f"Failed to fetch initial system data: {e}")


    def update_initial_data(self, initial_data):
        global data
        data.update(initial_data)
        self.update_gui()


    def start_websocket_connection(self):
        try:
            response = requests.post(HTTP_URL, json={'connection': 'monitor'})
            worker = response.json()
            self.start_websocket(worker['id'])
        except requests.RequestException as e:
            print(f"Failed to obtain worker ID: {e}")


    def start_websocket(self, worker_id):
        self.worker_id = worker_id
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(f"{WS_URL}{worker_id}",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        self.after(2000, self.update_gui)


    def on_message(self, ws, message):
        new_data = json.loads(message)
        self.update_live_data(new_data)


    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")


    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")


    def on_open(self, ws):
        print("WebSocket connection opened")


    def update_live_data(self, new_data):
        global data
        data['cpu'] = new_data.get('cpu', data['cpu'])
        data['mem'] = new_data.get('mem', data['mem'])
        data['disk'] = new_data.get('disk', data['disk'])
        data['user'] = new_data.get('user', data['user'])
        data['platform']['uptime'] = new_data.get('uptime', data['uptime'])
        data['processes'] = new_data.get('processes', data['processes'])


    def update_gui(self):
        self.update_section(self.platform_frame, data['platform'], [('distro', '', 'icon'), ('kernel', 'Kernel:'), ('uptime', 'Up:')])
        self.update_section(self.disk_frame, data['disk'], [('used', 'Used:', 'GB'), ('free', 'Free:', 'GB'), ('percent', 'Usage:', '%')])
        self.update_section(self.cpu_frame, data['cpu'], [('temp', 'Temperature:', '°C'), ('freq', 'Frequency:', 'MHz'), ('usage', 'Usage:', '%')])
        self.update_section(self.mem_frame, data['mem'], [('used', 'Used:', 'GB'), ('free', 'Free:', 'GB'), ('percent', 'Usage:', '%')])
        self.update_processes(data['processes'])
        self.after(2000, self.update_gui)


    def update_section(self, frame, data, fields):
        for widget in frame.winfo_children():
            widget.destroy()
        for key, label, *meta in fields:
            value = data.get(key, '')
            if meta and meta[0] and meta[0] == 'icon':
                self.add_label_with_icon(frame, label, value)
            elif meta and meta[0]:
                self.add_label(frame, label, f"{value} {meta[0]}".strip())
            else:
                self.add_label(frame, label, f"{value}".strip())


    def update_processes(self, processes):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, process in enumerate(processes):
            values = (process['pid'], process['name'], process['username'], process['mem'])
            tag = "odd" if i % 2 == 0 else "even"
            self.tree.insert("", "end", values=values, tags=(tag,))


    def on_closing(self):
        if self.ws:
            self.ws.close()
        if self.ws_thread:
            self.ws_thread.join()
        IOLoop.instance().add_callback(IOLoop.instance().stop)
        self.destroy()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    tornado_thread = threading.Thread(target=start_server)
    tornado_thread.daemon = True
    tornado_thread.start()
    app = SystemMonitorApp(data)
    app.mainloop()
