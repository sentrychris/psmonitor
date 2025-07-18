from tkinter import BooleanVar, IntVar, StringVar, Toplevel
import tkinter.ttk as ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app_manager import PSMonitorApp


class PSMonitorSettings:
    """
    Settings handler.
    """

    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    def __init__(self, manager: 'PSMonitorApp' = None) -> None:
        """
        Initializes the handler.
        """

        self._window_title = "View/Edit Settings"
        self._manager = manager

        # settnings
        self.logging_enabled = BooleanVar(value=True)
        self.log_level = StringVar(value="INFO")
        self.port_number = IntVar(value=4500)
        self.max_connections = IntVar(value=10)


    def open_window(self) -> None:
        """
        Open graph window.
        """

        if hasattr(self, '_window') and self._window.winfo_exists():
            if not self._window.winfo_viewable():
                self._window.deiconify()
            self._window.lift()
            return

        self._window = Toplevel(self._manager)
        self._window.title(self._window_title)
        self._window.geometry("450x500")
        self._window.resizable(False, False)
        self._window.protocol("WM_DELETE_WINDOW", self.on_close)

        main_frame = ttk.Frame(self._window, padding=10)
        main_frame.pack(fill="both", expand=True)

        self._build_logging_section(main_frame)
        self._build_server_section(main_frame)
        self._build_buttons_section(main_frame)


    def _build_logging_section(self, parent):
        logging_frame = ttk.LabelFrame(parent, text="Logging", padding=10)
        logging_frame.pack(fill="x", pady=10)

        # Logging enabled checkbox
        ttk.Checkbutton(
            logging_frame,
            text="Enable Logging",
            variable=self.logging_enabled
        ).pack(anchor="w")

        ttk.Label(
            logging_frame,
            text="When enabled, logs will be stored for diagnostic purposes."
        ).pack(anchor="w", pady=(2, 10))

        # Log level dropdown
        ttk.Label(logging_frame, text="Minimum Log Level:").pack(anchor="w")
        ttk.Combobox(
            logging_frame,
            textvariable=self.log_level,
            values=self.LOG_LEVELS,
            state='readonly'
        ).pack(anchor="w", fill="x", pady=5)

        # Buttons
        buttons_frame = ttk.Frame(logging_frame)
        buttons_frame.pack(fill="x", pady=5)

        ttk.Button(buttons_frame, text="Clear Log", command=self._manager.logger.clear_log).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame, text="Open Log", command=self._manager.logger.open_log).pack(side="left")


    def _build_server_section(self, parent):
        server_frame = ttk.LabelFrame(parent, text="Server", padding=10)
        server_frame.pack(fill="x", pady=10)

        # Port
        ttk.Label(server_frame, text="Port Number:").pack(anchor="w")
        ttk.Entry(server_frame, textvariable=self.port_number).pack(anchor="w", fill="x", pady=(0, 5))

        # Max connections
        ttk.Label(server_frame, text="Max Connections:").pack(anchor="w")
        ttk.Entry(server_frame, textvariable=self.max_connections).pack(anchor="w", fill="x", pady=(0, 5))

        ttk.Button(
            server_frame,
            text="Save & Restart Server",
            command=lambda: 1
        ).pack(anchor="e", pady=(10, 0))


    def _build_buttons_section(self, parent):
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(side="bottom", fill="x", pady=20)

        ttk.Button(
            buttons_frame,
            text="Apply",
            command=lambda: 1
        ).pack(side="left", padx=10)

        save_btn = ttk.Button(
            buttons_frame,
            text="Save",
            command=lambda: 1
        )
        save_btn.pack(side="right", padx=10)
        save_btn.bind("<Enter>", lambda e: self._show_tooltip("Settings will take effect next time you launch the app"))
        save_btn.bind("<Leave>", lambda e: self._hide_tooltip())

    
    def _show_tooltip(self, text):
        if not hasattr(self, '_tooltip'):
            self._tooltip = Toplevel(self._window)
            self._tooltip.wm_overrideredirect(True)
            self._tooltip.attributes("-topmost", True)
            label = ttk.Label(self._tooltip, text=text, background="lightyellow", borderwidth=1, relief="solid", padding=5)
            label.pack()

        x, y = self._window.winfo_pointerxy()
        self._tooltip.geometry(f"+{x+10}+{y+10}")
        self._tooltip.deiconify()


    def _hide_tooltip(self):
        if hasattr(self, '_tooltip'):
            self._tooltip.withdraw()


    def close_window(self) -> None:
        """
        Close window.
        """

        if hasattr(self, '_window') and self._window.winfo_exists():
            self.on_close()


    def on_close(self):
        """
        On close handler
        """
        # Destroy the window to free Tk resources
        self._window.destroy()

        # Optionally delete the _window reference
        del self._window
