import json
import logging
import os.path
import requests
import signal
import sys
import uuid
import websocket
import webbrowser
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


# Logger
logger = logging.getLogger(__name__)


def configure_logger(logfile: str):
    """
    Configures the logger to write logs to a specified file.
    
    Args:
        logfile (str): The name of the logfile.
    """
    filepath = os.path.join(os.path.expanduser('~'), '.psmonitor-logs')

    if not os.path.isdir(filepath):
        os.mkdir(filepath)

    destination = os.path.join(filepath, logfile)
    logging.basicConfig(filename=destination, level=logging.INFO)


def start_server():
    """
    Starts the server and listens on port 4500.
    """

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


class PSMonitorApp(tk.Tk):
    """
    GUI application for system monitoring.
    
    Attributes:
        data (dict): Initial data to populate the UI.
    """

    def __init__(self, data):
        """
        Initializes the app with initial data.
        
        Args:
            data (dict): Initial data to populate the UI.
        """
    
        super().__init__() # run tk.TK constructor
        self.title("PSMonitor - System monitoring utility")
        self.geometry("460x480")
        self.resizable(True, True)
        self.image_cache = {}

        app_icon = os.path.join(BASE_DIR, 'public', 'assets', 'icons', 'psmonitor.png')
        self.set_window_icon(app_icon)
        self.create_widgets(data)
        self.create_menu()
        self.ws = None
        self.ws_thread = None

        self.fetch_initial_data()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def set_window_icon(self, icon_path):
        """
        Sets the window icon.

        Args:
            icon_path (str): Path to the icon file.
        """

        icon = Image.open(icon_path)
        icon = icon.resize((32, 32), Image.LANCZOS)
        icon_photo = ImageTk.PhotoImage(icon)
        self.iconphoto(True, icon_photo)


    def create_widgets(self, data):
        """
        Creates and arranges the widgets in the application.

        Args:
            data (dict): Initial data to populate the widgets.
        """

        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=5, pady=5)

        self.platform_frame = self.create_section_frame(main_frame, "Platform")
        self.platform_labels = {
            "distro": self.add_label_with_icon(self.platform_frame, "", data['platform']['distro']),
            "kernel": self.add_label(self.platform_frame, "Kernel:", data['platform']['kernel']),
            "uptime": self.add_label(self.platform_frame, "Up:", data['platform']['uptime'])
        }
        self.platform_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.disk_frame = self.create_section_frame(main_frame, "Disk")
        self.disk_labels = {
            "used": self.add_label(self.disk_frame, "Used:", f"{data['disk']['used']} GB", "GB"),
            "free": self.add_label(self.disk_frame, "Free:", f"{data['disk']['free']} GB", "GB"),
            "percent": self.add_label(self.disk_frame, "Usage:", f"{data['disk']['percent']} %", "%")
        }
        self.disk_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.cpu_frame = self.create_section_frame(main_frame, "CPU")
        self.cpu_labels = {
            "temp": self.add_label(self.cpu_frame, "Temperature:", f"{data['cpu']['temp']} °C", "°C"),
            "freq": self.add_label(self.cpu_frame, "Frequency:", f"{data['cpu']['freq']} MHz", "MHz"),
            "usage": self.add_label(self.cpu_frame, "Usage:", f"{data['cpu']['usage']} %", "%")
        }
        self.cpu_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.mem_frame = self.create_section_frame(main_frame, "Memory")
        self.mem_labels = {
            "used": self.add_label(self.mem_frame, "Used:", f"{data['mem']['used']} GB", "GB"),
            "free": self.add_label(self.mem_frame, "Free:", f"{data['mem']['free']} GB", "GB"),
            "percent": self.add_label(self.mem_frame, "Usage:", f"{data['mem']['percent']} %", "%")
        }
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


    def create_menu(self):
        """
        Creates the menu bar.
        """

        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        
        help_menu.add_command(label="About", command=self.show_about)
        file_menu.add_command(label="Open Websocket Test Page..", command=self.open_websocket_page)
        file_menu.add_command(label="Close & Exit", command=self.on_closing)

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)


    def show_about(self):
        """
        Displays the 'About' window.
        """

        about_window = tk.Toplevel(self)
        about_window.title("About PSMonitor")
        about_window.geometry("400x400")
        about_window.resizable(False, False)

        label_version = ttk.Label(about_window, text="PSMonitor - A Simple System Monitor", font=("Arial", 10, "bold"))
        label_version.pack(pady=3)

        label_version = ttk.Label(about_window, text="Version 1.3.2", font=("Arial", 8, "bold"))
        label_version.pack(pady=1)

        label_github = ttk.Label(about_window, text="View the source code on Github", font=("Arial", 8), foreground="blue", cursor="hand2")
        label_github.pack(pady=1)
        label_github.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/sentrychris/psmonitor"))

        # White indented license frame
        license_frame = tk.Frame(about_window, bg="white", bd=2, relief="sunken")
        license_frame.pack(padx=10, pady=10, fill="both", expand=True)

        license_text = (
            "MIT License\n\n"
            "Copyright (c) 2025 Chris Rowles\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
            "of this software and associated documentation files (the \"Software\"), to deal\n"
            "in the Software without restriction, including without limitation the rights\n"
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
            "copies of the Software, and to permit persons to whom the Software is\n"
            "furnished to do so, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in all\n"
            "copies or substantial portions of the Software.\n\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
            "SOFTWARE."
        )

        text_widget = tk.Text(license_frame, bg="white", relief="flat", wrap="word", font=("Courier", 8))
        text_widget.insert("1.0", license_text)
        text_widget.config(state="disabled")  # Make read-only
        text_widget.pack(fill="both", expand=True, padx=5, pady=5)


    def create_section_frame(self, parent, title):
        """
        Creates a section frame within the parent frame.

        Args:
            parent (tk.Widget): The parent widget.
            title (str): The title of the section frame.
        
        Returns:
            ttk.LabelFrame: The created section frame.
        """

        section_frame = ttk.LabelFrame(parent, text=title)
        section_frame.grid(sticky="nsew", padx=5, pady=5)

        return section_frame


    def add_label(self, frame, text, value, suffix=""):
        """
        Adds a label to the specified frame.

        Args:
            frame (tk.Widget): The parent frame.
            text (str): The label text.
            value (str): The value to be displayed.
            suffix (str, optional): The suffix for the label text.
        
        Returns:
            tuple: The created label and suffix.
        """

        label_text = f"{text} {value} {suffix}".strip()
        label = ttk.Label(frame, text=label_text)
        label.grid(sticky='w', padx=5, pady=2)

        return label, suffix


    def load_image(self, path, width):
        """
        Loads an image from the specified path and resizes it.

        Args:
            path (str): The path to the image file.
            width (int): The desired width of the image.
        
        Returns:
            ImageTk.PhotoImage: The loaded and resized image.
        """

        if path in self.image_cache:
            return self.image_cache[path]
        image = Image.open(path)
        image = image.resize((width, int(image.height * width / image.width)), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image_cache[path] = photo

        return photo


    def add_label_with_icon(self, frame, text, value):
        """
        Adds a label with an icon to the specified frame.

        Args:
            frame (tk.Widget): The parent frame.
            text (str): The label text.
            value (str): The value to be displayed.
        
        Returns:
            ttk.Label: The created label.
        """

        container = ttk.Frame(frame)
        container.grid(sticky='w', padx=5, pady=2)
        icon_file = 'windows.png'
        icon_width = 14
        if sys.platform == 'linux':
            icon_width = 18
            icon_file = 'linux.png'
        png_path = os.path.join(BASE_DIR, 'public', 'assets', 'icons', icon_file)
        photo = self.load_image(png_path, icon_width)
        icon_label = ttk.Label(container, image=photo)
        icon_label.image = photo
        icon_label.pack(side=tk.LEFT)
        text_label = ttk.Label(container, text=f"{value}")
        text_label.pack(side=tk.LEFT)

        return text_label


    def add_processes_table(self, frame, processes_data):
        """
        Adds a table to display process information.

        Args:
            frame (tk.Widget): The parent frame.
            processes_data (list): The list of processes data.
        """

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
        """
        Fetches the initial system data from the server.
        """

        try:
            response = requests.get(f'{HTTP_URL}/system')
            initial_data = response.json()
            self.update_initial_data(initial_data)
            self.start_websocket_connection()
        except requests.RequestException as e:
            logger.error(f"Error fetching initial system data: {e}")


    def update_initial_data(self, initial_data):
        """
        Updates the initial data in the application.

        Args:
            initial_data (dict): The initial data to update.
        """

        global data
        data.update(initial_data)
        self.update_gui()


    def start_websocket_connection(self):
        """
        Starts the websocket connection for live data updates.
        """

        try:
            response = requests.post(HTTP_URL, json={'connection': 'monitor'})
            worker = response.json()
            self.start_websocket(worker['id'])
        except requests.RequestException as e:
            logger.error(f"Error obtaining worker for websocket connection: {e}")


    def start_websocket(self, worker_id):
        """
        Starts the websocket connection with the specified worker ID.

        Args:
            worker_id (str): The worker ID for the websocket connection.
        """

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
        self.after(1000, self.update_gui)


    def on_message(self, ws, message):
        """
        Handles incoming websocket messages.

        Args:
            ws (websocket.WebSocketApp): The websocket instance.
            message (str): The incoming message.
        """

        try:
            new_data = json.loads(message)
            self.update_live_data(new_data)
        except Exception as e:
            logger.error(f"Error fetching websocket data: {e}")


    def on_error(self, ws, error):
        """
        Handles websocket errors.

        Args:
            ws (websocket.WebSocketApp): The websocket instance.
            error (Exception): The error encountered.
        """

        print(f"WebSocket error: {error}")


    def on_close(self, ws, close_status_code, close_msg):
        """
        Handles websocket closure.

        Args:
            ws (websocket.WebSocketApp): The websocket instance.
            close_status_code (int): The status code for the closure.
            close_msg (str): The closure message.
        """

        print("WebSocket closed")


    def on_open(self, ws):
        """
        Handles websocket opening.

        Args:
            ws (websocket.WebSocketApp): The websocket instance.
        """

        print("WebSocket connection opened")


    def update_live_data(self, new_data):
        """
        Updates the live data in the application.

        Args:
            new_data (dict): The new data to update.
        """

        global data
        data['cpu'] = new_data.get('cpu', data['cpu'])
        data['mem'] = new_data.get('mem', data['mem'])
        data['disk'] = new_data.get('disk', data['disk'])
        data['user'] = new_data.get('user', data['user'])
        data['platform']['uptime'] = new_data.get('uptime', data['uptime'])
        data['processes'] = new_data.get('processes', data['processes'])


    def update_gui(self):
        """
        Updates the GUI with the latest data.
        """

        self.update_section(self.platform_labels, data['platform'])
        self.update_section(self.disk_labels, data['disk'])
        self.update_section(self.cpu_labels, data['cpu'])
        self.update_section(self.mem_labels, data['mem'])
        self.update_processes(data['processes'])
        self.after(1000, self.update_gui)


    def update_section(self, labels, data):
        """
        Updates a section of the GUI.

        Args:
            labels (dict): The labels in the section.
            data (dict): The data to update.
        """

        for key, value in data.items():
            if key in labels:
                if isinstance(labels[key], tuple):
                    label, suffix = labels[key]
                    label.config(text=f"{label.cget('text').split(':')[0]}: {value} {suffix}".strip())
                else:
                    label = labels[key]
                    if key == 'distro':
                        label.config(text=f"{value}".strip())
                    else:
                        label.config(text=f"{label.cget('text').split(':')[0]}: {value}".strip())


    def update_processes(self, processes):
        """
        Updates the processes table with new data.

        Args:
            processes (list): The list of processes to update.
        """

        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, process in enumerate(processes):
            values = (process['pid'], process['name'], process['username'], process['mem'])
            tag = "odd" if i % 2 == 0 else "even"
            self.tree.insert("", "end", values=values, tags=(tag,))


    def open_websocket_page(self):
        """
        Opens the websocket monitoring webpage in the default browser.
        """
        webbrowser.open_new("http://127.0.0.1:4500")


    def on_closing(self):
        """
        Handles application closing.
        """

        if self.ws:
            self.ws.close()
        if self.ws_thread:
            self.ws_thread.join()

        IOLoop.instance().add_callback(IOLoop.instance().stop)
        self.destroy()


if __name__ == "__main__":
    """
    Main entry point for the application.
    """

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if sys.platform == "darwin":
        print("MacOS is not supported.")
        exit(0)

    configure_logger(logfile='app.log')
    
    tornado_thread = threading.Thread(target=start_server)
    tornado_thread.daemon = True
    tornado_thread.start()

    data = {
        "cpu": {"usage": 0.0, "temp": 0, "freq": 0},
        "mem": {"total": 0, "used": 0, "free": 0, "percent": 0},
        "disk": {"total": 0, "used": 0, "free": 0, "percent": 0},
        "user": "",
        "platform": {"distro": "", "kernel": "", "uptime": ""},
        "uptime": "",
        "processes": []
    }
    
    app = PSMonitorApp(data)
    app.mainloop()
