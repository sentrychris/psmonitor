import tkinter as tk
from tkinter import ttk
import requests
import websocket
import threading
import json


data = {
    "cpu": {
        "usage": 0.0,
        "temp": 0,
        "freq": 0
    },
    "mem": {
        "total": 0,
        "used": 0,
        "free": 0,
        "percent": 0
    },
    "disk": {
        "total": 0,
        "used": 0,
        "free": 0,
        "percent": 0
    },
    "user": "",
    "platform": {
        "distro": "",
        "kernel": "",
        "uptime": ""
    },
    "processes": []
}

class SystemMonitorApp(tk.Tk):


    def __init__(self, data):
        super().__init__()
        self.title("System Monitor")
        self.geometry("450x480")
        self.create_widgets(data)
        self.ws = None

        # Fetch initial data and start WebSocket connection
        self.fetch_initial_data_and_connect()


    def create_widgets(self, data):
        # Create a main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=5, pady=5)

        # Platform Section
        self.platform_frame = self.create_section_frame(main_frame, "Platform")
        self.add_label(self.platform_frame, "Distro:", data['platform']['distro'])
        self.add_label(self.platform_frame, "Kernel:", data['platform']['kernel'])
        self.add_label(self.platform_frame, "Up:", data['platform']['uptime'])
        self.platform_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Disk Section
        self.disk_frame = self.create_section_frame(main_frame, "Disk")
        self.add_label(self.disk_frame, "Used:", f"{data['disk']['used']} GB")
        self.add_label(self.disk_frame, "Free:", f"{data['disk']['free']} GB")
        self.add_label(self.disk_frame, "Usage:", f"{data['disk']['percent']} %")
        self.disk_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # CPU Section
        self.cpu_frame = self.create_section_frame(main_frame, "CPU")
        self.add_label(self.cpu_frame, "Temperature:", f"{data['cpu']['temp']} °C")
        self.add_label(self.cpu_frame, "Frequency:", f"{data['cpu']['freq']} MHz")
        self.add_label(self.cpu_frame, "Usage:", f"{data['cpu']['usage']} %")
        self.cpu_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Memory Section
        self.mem_frame = self.create_section_frame(main_frame, "Memory")
        self.add_label(self.mem_frame, "Used:", f"{data['mem']['used']} GB")
        self.add_label(self.mem_frame, "Free:", f"{data['mem']['free']} GB")
        self.add_label(self.mem_frame, "Usage:", f"{data['mem']['percent']} %")
        self.mem_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # Processes Section
        self.processes_frame = self.create_section_frame(main_frame, "Top Processes")
        self.add_processes_table(self.processes_frame, data['processes'])
        self.processes_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Make the grid cells expand proportionally
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


    def add_processes_table(self, frame, processes_data):
        columns = ("pid", "name", "username", "mem")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)

        # Set the heading and cell alignment to center, and set column width with minwidth
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


    def fetch_initial_data_and_connect(self):
        # Fetch initial system data
        try:
            response = requests.get('http://localhost:4500/system')
            initial_data = response.json()
            self.update_initial_data(initial_data)
        except requests.RequestException as e:
            print(f"Failed to fetch initial system data: {e}")
            return

        # Obtain worker ID via HTTP request
        try:
            response = requests.post('http://localhost:4500', json={'connection': 'monitor'})
            worker = response.json()

            # Start WebSocket connection with the obtained worker ID
            self.start_websocket(worker['id'])
        except requests.RequestException as e:
            print(f"Failed to obtain worker ID: {e}")


    def update_initial_data(self, initial_data):
        global data
        data.update(initial_data)
        self.update_gui()


    def start_websocket(self, worker_id):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(f"ws://localhost:4500/connect?id={worker_id}",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open

        # Run WebSocket in a separate thread
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

        # Schedule the GUI to update periodically
        self.after(1000, self.update_gui)


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
        # Only update the parts of the data that are received via WebSocket
        data['cpu'] = new_data.get('cpu', data['cpu'])
        data['mem'] = new_data.get('mem', data['mem'])
        data['disk'] = new_data.get('disk', data['disk'])
        data['user'] = new_data.get('user', data['user'])
        data['platform']['uptime'] = new_data.get('platform', {}).get('uptime', data['platform']['uptime'])
        data['processes'] = new_data.get('processes', data['processes'])


    def update_gui(self):
        # Update Platform Section (only uptime, leave distro and kernel as is)
        for widget in self.platform_frame.winfo_children():
            widget.destroy()
        self.add_label(self.platform_frame, "Distro:", data['platform']['distro'])
        self.add_label(self.platform_frame, "Kernel:", data['platform']['kernel'])
        self.add_label(self.platform_frame, "Up:", data['platform']['uptime'])

        # Update Disk Section
        for widget in self.disk_frame.winfo_children():
            widget.destroy()
        self.add_label(self.disk_frame, "Used:", f"{data['disk']['used']} GB")
        self.add_label(self.disk_frame, "Free:", f"{data['disk']['free']} GB")
        self.add_label(self.disk_frame, "Usage:", f"{data['disk']['percent']} %")

        # Update CPU Section
        for widget in self.cpu_frame.winfo_children():
            widget.destroy()
        self.add_label(self.cpu_frame, "Temperature:", f"{data['cpu']['temp']} °C")
        self.add_label(self.cpu_frame, "Frequency:", f"{data['cpu']['freq']} MHz")
        self.add_label(self.cpu_frame, "Usage:", f"{data['cpu']['usage']} %")

        # Update Memory Section
        for widget in self.mem_frame.winfo_children():
            widget.destroy()
        self.add_label(self.mem_frame, "Used:", f"{data['mem']['used']} GB")
        self.add_label(self.mem_frame, "Free:", f"{data['mem']['free']} GB")
        self.add_label(self.mem_frame, "Usage:", f"{data['mem']['percent']} %")

        # Update Processes Section
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, process in enumerate(data['processes']):
            values = (process['pid'], process['name'], process['username'], process['mem'])
            tag = "odd" if i % 2 == 0 else "even"
            self.tree.insert("", "end", values=values, tags=(tag,))

        # Schedule the next update
        self.after(1000, self.update_gui)


if __name__ == "__main__":
    app = SystemMonitorApp(data)
    app.mainloop()
