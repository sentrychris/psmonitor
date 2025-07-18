
import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
import webbrowser

from PIL import Image, ImageTk
from typing import TYPE_CHECKING

# Typing (type hints only, no runtime dependency)
if TYPE_CHECKING:
    from .log_handler import PSMonitorAppLogger

# Local application imports
from .app_client import PSMonitorAppClient
from .graph_handler import PSMonitorGraphHandler
from .settings_handler import PSMonitorSettings


# Constants
BASE_DIR = os.path.dirname(__file__)
UPDATE_INTERVAL = 1000


class PSMonitorApp(tk.Tk):
    """
    GUI application for system monitoring.
    """

    def __init__(self, data: dict, logger: 'PSMonitorAppLogger' = None) -> None:
        """
        Initializes the app with initial data.
        """

        super().__init__()

        # Must be initiialized before others and in the following order
        self.data = data
        self.logger = logger
        self.settings = PSMonitorSettings(self)
        # End initialization

        self.client = PSMonitorAppClient(self)

        self.graph_handler = PSMonitorGraphHandler(self)

        self.cpu_temp_graph = self.graph_handler.create_graph(
            key="cpu",
            metric="temp",
            y_label="CPU Temp. (C°)",
            title="CPU Temperature Graph"
        )

        self.cpu_usage_graph = self.graph_handler.create_graph(
            key="cpu",
            metric="usage",
            y_label="CPU Usage (%)",
            title="CPU Usage Graph"
        )

        self.mem_usage_graph = self.graph_handler.create_graph(
            key="mem",
            metric="percent",
            y_label="Mem. Usage (%)",
            title="Memory Usage Graph"
        )

        self.max_process_rows = 10
        self.cached_processes = [("", "", "", "") for _ in range(self.max_process_rows)]

        self.title("psmonitor - A system monitor")
        self.geometry("460x480")
        self.resizable(True, True)
        self.image_cache = {}

        self.platform_icons = {}

        platform_icon_defs = {
            "linux":   ("linux.png", 18),
            "windows": ("windows.png", 14),
        }

        for platform, (filename, width) in platform_icon_defs.items():
            path = os.path.join(BASE_DIR, 'assets', 'icons', filename)
            self.platform_icons[platform] = self.load_image(path, width)

        self.set_window_icon(os.path.join(BASE_DIR, 'assets', 'icons', 'psmonitor.png'))
        self.create_gui_menu()
        self.create_gui_sections(data)
        
        self.client.setup_connection()

        self.protocol("WM_DELETE_WINDOW", self.client.on_closing)


    def set_window_icon(self, icon_path: str) -> str:
        """
        Sets the window icon.

        Args:
            icon_path (str): Path to the icon file.
        """

        icon = Image.open(icon_path)
        icon = icon.resize((32, 32), Image.LANCZOS)
        icon_photo = ImageTk.PhotoImage(icon)
        self.iconphoto(True, icon_photo)


    def create_gui_menu(self) -> None:
        """
        Creates the menu bar.
        """

        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About...", command=self.open_about_window)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open web UI...", command=self.open_web_ui)
        file_menu.add_command(label="Open app log...", command=self.logger.open_log)
        file_menu.add_separator()
        file_menu.add_command(label="Open Settings", command=self.settings.open_window)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.client.on_closing)

        graphs_menu = tk.Menu(menu_bar, tearoff=0)
        graphs_cpu_submenu = tk.Menu(graphs_menu, tearoff=0)
        graphs_mem_submenu = tk.Menu(graphs_menu, tearoff=0)
    
        graphs_cpu_submenu.add_command(label="Temperature Graph", command=self.cpu_temp_graph.open_window)
        graphs_cpu_submenu.add_command(label="Usage Graph", command=self.cpu_usage_graph.open_window)
        graphs_menu.add_cascade(label="CPU", menu=graphs_cpu_submenu)

        graphs_mem_submenu.add_command(label="Usage Graph", command=self.mem_usage_graph.open_window)
        graphs_menu.add_cascade(label="Memory", menu=graphs_mem_submenu)

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Graphs ", menu=graphs_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)


    def create_gui_sections(self, data: dict) -> None:
        """
        Creates and arranges the sections in the application.

        Args:
            data (dict): Initial data to populate the widgets.
        """

        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=5, pady=5)

        def make_labels(frame, defs):
            return {k: v(frame) for k, v in defs.items()}

        sections = [
            ("platform", 0, 0, {
                "distro": lambda f: self.create_label_with_icon(f, "", data["platform"]["distro"]),
                "kernel": lambda f: self.create_label(f, "Kernel:", data["platform"]["kernel"]),
                "uptime": lambda f: self.create_label(f, "Up:", data["platform"]["uptime"]),
            }),
            ("disk", 0, 1, {
                "used": lambda f: self.create_label(f, "Used:", f"{data['disk']['used']} GB", "GB"),
                "free": lambda f: self.create_label(f, "Free:", f"{data['disk']['free']} GB", "GB"),
                "percent": lambda f: self.create_label(f, "Usage:", f"{data['disk']['percent']} %", "%"),
            }),
            ("cpu", 1, 0, {
                "temp": lambda f: self.create_label(f, "Temperature:", f"{data['cpu']['temp']} °C", "°C"),
                "freq": lambda f: self.create_label(f, "Frequency:", f"{data['cpu']['freq']} MHz", "MHz"),
                "usage": lambda f: self.create_label(f, "Usage:", f"{data['cpu']['usage']} %", "%"),
            }),
            ("mem", 1, 1, {
                "used": lambda f: self.create_label(f, "Used:", f"{data['mem']['used']} GB", "GB"),
                "free": lambda f: self.create_label(f, "Free:", f"{data['mem']['free']} GB", "GB"),
                "percent": lambda f: self.create_label(f, "Usage:", f"{data['mem']['percent']} %", "%"),
            }),
        ]

        for name, r, c, defs in sections:
            section_frame = self.create_gui_section(main_frame, name.upper() if name == "cpu" else name.capitalize())
            section_frame.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
            setattr(self, f"{name}_frame", section_frame)
            setattr(self, f"{name}_labels", make_labels(section_frame, defs))

        self.processes_frame = self.create_gui_section(main_frame, "Top Processes")
        self.processes_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=(5, 0), sticky="nsew")
        self.create_processes_table(self.processes_frame, data['processes'])

        for i in range(4):
            main_frame.rowconfigure(i, weight=1)
        for i in range(2):
            main_frame.columnconfigure(i, weight=1)


    def create_gui_section(self, parent: ttk.Frame, title: str) -> ttk.LabelFrame:
        """
        Creates a section frame within the parent frame.

        Args:
            parent (ttk.Frame): The parent frame.
            title (str): The title of the section frame.
        
        Returns:
            ttk.LabelFrame: The created section frame.
        """

        section_frame = ttk.LabelFrame(parent, text=title)
        section_frame.grid(sticky="nsew", padx=5, pady=5)

        return section_frame


    def update_gui_sections(self) -> None:
        """
        Updates the GUI with the latest data.
        """

        self.update_gui_section(self.platform_labels, self.data['platform'])
        self.update_gui_section(self.disk_labels, self.data['disk'])
        self.update_gui_section(self.cpu_labels, self.data['cpu'])
        self.update_gui_section(self.mem_labels, self.data['mem'])

        self.update_processes_table()
        self.graph_handler.update_active_graphs()

        # schedule function to call itself again
        self.after(UPDATE_INTERVAL, self.update_gui_sections)


    def update_gui_section(self, labels: dict, data: dict) -> None:
        """
        Updates a section of the GUI.

        Args:
            labels (dict): The labels in the section.
            data (dict): The data to update.
        """

        for key, value in data.items():
            if key not in labels:
                continue

            if isinstance(labels[key], tuple):
                label, suffix = labels[key]
                new_text = f"{label.prefix} {value} {suffix}".strip()
            else:
                label = labels[key]
                if key == 'distro':
                    new_text = f"{value}".strip()
                else:
                    new_text = f"{label.prefix} {value}".strip()

            if label["text"] != new_text:
                label.config(text=new_text)


    def open_about_window(self) -> None:
        """
        Displays the 'About' window.
        """

        about_window = tk.Toplevel(self)
        about_window.title("About psmonitor")
        about_window.geometry("400x400")
        about_window.resizable(False, False)

        label_version = ttk.Label(about_window, text="psmonitor - A simple system monitor.", font=("Arial", 10, "bold"))
        label_version.pack(pady=3)

        label_version = ttk.Label(about_window, text="Version 1.5.0.1001", font=("Arial", 8, "bold"))
        label_version.pack(pady=1)

        label_github = ttk.Label(about_window, text="View the source code on Github", font=("Arial", 8), foreground="blue", cursor="hand2")
        label_github.pack(pady=1)
        label_github.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/sentrychris/psmonitor"))

        # White indented license frame - uses classic tk.Frame instead for bg
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


    def open_web_ui(self) -> None:
        """
        Opens the web UI for testing the websocket connection.
        """
        webbrowser.open_new("http://127.0.0.1:4500")


    def create_processes_table(self, frame: ttk.Frame, processes_data: list) -> None:
        """
        Adds a table to display process information.

        Args:
            frame (ttk.Frame): The parent frame.
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

        # create empty fixed rows
        for i in range(self.max_process_rows):
            tag = "odd" if i % 2 == 0 else "even"
            self.tree.insert("", "end", iid=f"proc{i}", values=("", "", "", ""), tags=(tag,))

        self.tree.tag_configure("odd", background="lightgrey")
        self.tree.tag_configure("even", background="white")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)


    def update_processes_table(self) -> None:
        """
        Updates the processes table with new data.

        Args:
            processes (list): The list of processes to update.
        """

        for i in range(self.max_process_rows):
            if i < len(self.data['processes']):
                process = self.data['processes'][i]
                values = (
                    process.get("pid", ""),
                    process.get("name", ""),
                    process.get("username", ""),
                    process.get("mem", "")
                )
            else:
                values = ("", "", "", "")

            if values != self.cached_processes[i]:
                self.tree.item(f"proc{i}", values=values)
                self.cached_processes[i] = values


    def create_label(self, frame: ttk.Frame, text: str, value: str, suffix: str = "") -> tuple[ttk.Label, str]:
        """
        Adds a label to the specified frame.

        Args:
            frame (ttk.Frame): The parent frame.
            text (str): The label text.
            value (str): The value to be displayed.
            suffix (str, optional): The suffix for the label text.
        
        Returns:
            tuple: The created label and suffix.
        """

        label_text = f"{text} {value} {suffix}".strip()
        label = ttk.Label(frame, text=label_text)
        label.grid(sticky='w', padx=5, pady=2)
        label.prefix = text

        return label, suffix


    def create_label_with_icon(self, frame: ttk.Frame, text: str, value: str) -> ttk.Label:
        """
        Adds a label with an icon to the specified frame.

        Args:
            frame (ttk.Frame): The parent frame.
            text (str): The label text.
            value (str): The value to be displayed.
        
        Returns:
            ttk.Label: The created label.
        """

        container = ttk.Frame(frame)
        container.grid(sticky='w', padx=5, pady=2)

        platform_key = 'linux' if sys.platform == 'linux' else 'windows'
        icon = self.platform_icons[platform_key]

        icon_label = ttk.Label(container, image=icon)
        icon_label.image = icon
        icon_label.pack(side='left')

        text_label = ttk.Label(container, text=f"{value}")
        text_label.pack(side='left')

        return text_label
    

    def load_image(self, path: str, width: int) -> ImageTk.PhotoImage:
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


    def refresh_data(self, new_data: dict) -> None:
        """
        Updates the data in the application.

        Args:
            new_data (dict): The new data to update.
        """

        self.data['cpu'] = new_data.get('cpu', self.data['cpu'])
        self.data['mem'] = new_data.get('mem', self.data['mem'])
        self.data['disk'] = new_data.get('disk', self.data['disk'])
        self.data['user'] = new_data.get('user', self.data['user'])
        self.data['platform']['uptime'] = new_data.get('uptime', self.data['uptime'])
        self.data['processes'] = new_data.get('processes', self.data['processes'])
