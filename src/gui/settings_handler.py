"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: settings_handler.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.5.0.2413
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import json
import os
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

# Local application imports
from core.config import DEFAULT_LOG_ENABLED, DEFAULT_LOG_LEVEL, \
    DEFAULT_ADDRESS, DEFAULT_PORT, DEFAULT_MAX_WS_CONNECTIONS, \
        DEFAULT_MAX_RECONNECT_ATTEMPTS, DEFAULT_RECONNECT_BASE_DELAY, \
            DEFAULT_GUI_REFRESH_INTERVAL, SETTINGS_FILE, read_settings_file

# Typing (type hints only, no runtime dependency)
if TYPE_CHECKING:
    from gui.app_manager import PSMonitorApp


class PSMonitorAppSettingsHandler:
    """
    Settings handler.
    """

    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

    def __init__(self, manager: 'PSMonitorApp' = None) -> None:
        """
        Initializes the handler.
        """

        self._window = None
        self._window_title = "View/Edit Settings"

        self._log_status_label = None
        self._settings_status_label = None
        self._server_status_label = None
        self._tooltip = None

        self._manager = manager

        # Default settings
        self.logging_enabled = tk.BooleanVar(value=DEFAULT_LOG_ENABLED)
        self.log_level = tk.StringVar(value=DEFAULT_LOG_LEVEL)
        self.address = tk.StringVar(value=DEFAULT_ADDRESS)
        self.port_number = tk.IntVar(value=DEFAULT_PORT)
        self.max_ws_connections = tk.IntVar(value=DEFAULT_MAX_WS_CONNECTIONS)
        self.max_reconnect_attempts = tk.IntVar(value=DEFAULT_MAX_RECONNECT_ATTEMPTS)
        self.reconnect_base_delay = tk.DoubleVar(value=DEFAULT_RECONNECT_BASE_DELAY)
        self.gui_refresh_interval = tk.IntVar(value=DEFAULT_GUI_REFRESH_INTERVAL)

        # Load saved settings
        self._load_settings_from_file()


    def open_window(self) -> None:
        """
        Open graph window.
        """

        if hasattr(self, '_window') and self._window and self._window.winfo_exists():
            if not self._window.winfo_viewable():
                self._window.deiconify()
            self._window.lift()
            return

        self._window = tk.Toplevel(self._manager)
        self._window.title(self._window_title)
        self._window.geometry("450x630")
        self._window.resizable(False, False)
        self._window.protocol("WM_DELETE_WINDOW", self.on_close)

        main_frame = ttk.Frame(self._window, padding=10)
        main_frame.pack(fill="both", expand=True)

        self._build_logging_section(main_frame)
        self._build_server_section(main_frame)
        self._build_save_close_buttons_section(main_frame)


    def get_current_settings(self):
        """
        Get the current settings
        """

        return {
            "logging_enabled": self.logging_enabled.get(),
            "log_level": self.log_level.get(),
            "address": self.address.get(),
            "port_number": self.port_number.get(),
            "max_ws_connections": self.max_ws_connections.get(),
            "max_reconnect_attempts": self.max_reconnect_attempts.get(),
            "reconnect_base_delay": self.reconnect_base_delay.get(),
            "gui_refresh_interval": self.gui_refresh_interval.get()
        }


    def _build_logging_section(self, parent):
        """
        Build the logging section
        """

        logging_frame = ttk.LabelFrame(parent, text="Logging", padding=10)
        logging_frame.pack(fill="x", pady=(0, 10))

        # Logging enabled checkbox
        ttk.Checkbutton(
            logging_frame,
            text="Enable logging",
            variable=self.logging_enabled
        ).pack(anchor="w")

        ttk.Label(
            logging_frame,
            text="When enabled, logs will be stored for diagnostic purposes."
        ).pack(anchor="w", pady=(2, 10))

        # Log level dropdown
        ttk.Label(logging_frame, text="Minimum log level:").pack(anchor="w")
        ttk.Combobox(
            logging_frame,
            textvariable=self.log_level,
            values=self.LOG_LEVELS,
            state='readonly'
        ).pack(anchor="w", fill="x", pady=5)

        # Buttons
        log_buttons_frame = ttk.Frame(logging_frame)
        log_buttons_frame.pack(fill="x", pady=5)

        ttk.Button(
            log_buttons_frame,
            text="Clear Log",
            command=self._on_clear_log
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            log_buttons_frame,
            text="Open Log",
            command=self._manager.logger.open_log
        ).pack(side="left")

        ttk.Button(
            log_buttons_frame,
            text="Save & Apply",
            command=self._on_save_and_apply_logging_settings
        ).pack(side="right", padx=(0, 5))

        self._log_status_label = ttk.Label(log_buttons_frame, text="", foreground="green")
        self._log_status_label.pack(side="left", padx=(10, 0))


    def _on_clear_log(self):
        """
        Handle clear log button
        """

        try:
            self._manager.logger.clear_log()
            self._show_logging_action_status("✔ Log has been cleared", "green", duration=2000)
        except Exception:
            self._show_logging_action_status("✖ Failed to clear log", "red", duration=2000)


    def _on_save_and_apply_logging_settings(self) -> None:
        """
        Save and apply logging settings.
        """

        self._save_settings_to_file()

        if self._manager:
            self._manager.logger.set_enabled(self.logging_enabled.get())
            self._manager.logger.set_level(self.log_level.get())
            self._show_logging_action_status("✔ Log settings applied", "green", 2000)


    def _build_server_section(self, parent):
        """
        Build the server section
        """

        server_frame = ttk.LabelFrame(parent, text="Server", padding=10)
        server_frame.pack(fill="x", pady=(0, 5))

        style = ttk.Style()
        style.configure("Help.TLabel", foreground="#333333", font=("Arial", 8))

        # Description label
        ttk.Label(
            server_frame,
            text="Configure the embedded server and websocket settings."
        ).pack(anchor="w", pady=(0, 10))

        # Port
        ttk.Label(server_frame, text="Port number:").pack(anchor="w")
        ttk.Entry(
            server_frame,
            textvariable=self.port_number,
        ).pack(anchor="w", fill="x", pady=(0, 5))

        ttk.Label(
            server_frame,
            text="Sets the port for the server to listen on for incoming connections.",
            wraplength=400,
            style="Help.TLabel"
        ).pack(anchor="w", pady=(0, 5))

        # Max connections
        ttk.Label(server_frame, text="Max allowed connections:").pack(anchor="w")
        ttk.Entry(
            server_frame,
            textvariable=self.max_ws_connections,
        ).pack(anchor="w", fill="x", pady=(0, 5))

        ttk.Label(
            server_frame,
            text="Sets the max number of allowed websocket connections to the server.",
            wraplength=400,
            style="Help.TLabel"
        ).pack(anchor="w", pady=(0, 5))

        # Max reconnect attempts
        ttk.Label(server_frame, text="Max reconnect attempts:").pack(anchor="w")
        ttk.Entry(
            server_frame,
            textvariable=self.max_reconnect_attempts,
        ).pack(anchor="w", fill="x", pady=(0, 5))

        ttk.Label(
            server_frame,
            text="Sets the max number of reconnection attempts to the server.",
            wraplength=400,
            style="Help.TLabel"
        ).pack(anchor="w", pady=(0, 5))

        # Max reconnect attempts
        ttk.Label(server_frame, text="Reconnect attempt delay:").pack(anchor="w")
        ttk.Entry(
            server_frame,
            textvariable=self.reconnect_base_delay,
        ).pack(anchor="w", fill="x", pady=(0, 5))

        ttk.Label(
            server_frame,
            text="Sets the base delay used in exponential backoff when reconnecting.",
            wraplength=400,
            style="Help.TLabel"
        ).pack(anchor="w", pady=(0, 5))

        # Buttons
        server_button_frame = ttk.Frame(server_frame)
        server_button_frame.pack(fill="x", pady=(0, 0))

        self._server_status_label = ttk.Label(server_button_frame, text="", foreground="green")
        self._server_status_label.pack(side="left", anchor="w", padx=(0, 5))

        ttk.Button(
            server_button_frame,
            text="Save & Apply",
            command=self._on_save_and_restart_server_settings
        ).pack(anchor="e", pady=(10, 0))


    def _on_save_and_restart_server_settings(self) -> None:
        """
        Save and restart the server.
        """

        self._save_settings_to_file()

        address = self.address.get()
        port = self.port_number.get()

        self._manager.client.close_websocket_connection()
        self._manager.client.set_address_and_port(address, port)
        self._manager.server.restart(port)
        self._manager.client.safe_connect()

        self._show_server_actions_status("✔ Settings applied and server restarted", "green", 2000)


    def _build_save_close_buttons_section(self, parent):
        """
        Build the save/close buttons section
        """

        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(side="bottom", fill="x", pady=(5, 10))

        # Status label
        self._settings_status_label = ttk.Label(buttons_frame, text="", foreground="green")
        self._settings_status_label.pack(side="left", expand=True)

        close_btn = ttk.Button(
            buttons_frame,
            text="Close",
            command=self.on_close
        )
        close_btn.pack(side="right", padx=10)

        save_btn = ttk.Button(
            buttons_frame,
            text="Save",
            command=self._on_save
        )
        save_btn.pack(side="right", padx=10)
        save_btn.bind(
            sequence="<Enter>",
            func=lambda e: self._show_tooltip("Will take effect next time you launch the app")
        )
        save_btn.bind(
            sequence="<Leave>",
            func=lambda e: self._hide_tooltip()
        )


    def _on_save(self):
        """
        Handle save button
        """

        success = self._save_settings_to_file()
        if success:
            self._show_save_action_status("✔ Settings saved", "green", 2000)
        else:
            self._show_save_action_status("✖ Failed to save settings", "red", 2000)


    def _show_logging_action_status(self, text: str, color: str, duration: int = 2000):
        """
        Show log actions status label
        """

        if hasattr(self, '_log_status_label'):
            self._log_status_label.config(text=text, foreground=color)
            self._window.after(duration, lambda: self._log_status_label.config(text=""))


    def _show_server_actions_status(self, text: str, color: str, duration: int = 2000):
        """
        Show actions status label
        """

        if hasattr(self, '_server_status_label'):
            self._server_status_label.config(text=text, foreground=color)
            self._window.after(duration, lambda: self._server_status_label.config(text=""))


    def _show_save_action_status(self, text: str, color: str, duration: int = 2000):
        """
        Show actions status label
        """

        if hasattr(self, '_settings_status_label'):
            self._settings_status_label.config(text=text, foreground=color)
            self._window.after(duration, lambda: self._settings_status_label.config(text=""))


    def _show_tooltip(self, text):
        """
        Show a tooltip
        """

        if self._tooltip is None and self._window:
            self._tooltip = tk.Toplevel(self._window)
            self._tooltip.wm_overrideredirect(True)
            self._tooltip.attributes("-topmost", True)
            label = ttk.Label(
                self._tooltip,
                text=text,
                background="lightyellow",
                borderwidth=1,
                relief="solid",
                padding=5
            )
            label.pack()

        x, y = self._window.winfo_pointerxy()
        self._tooltip.geometry(f"+{x+10}+{y+10}")
        self._tooltip.deiconify()


    def _hide_tooltip(self):
        """
        Hide a tooltip
        """

        if hasattr(self, '_tooltip'):
            self._tooltip.withdraw()


    def _load_settings_from_file(self) -> None:
        """
        Load settings from file if it exists.
        """

        if not os.path.exists(SETTINGS_FILE):
            self._manager.logger.error(f"Settings file does not exist at: {SETTINGS_FILE}")
            return

        settings = read_settings_file(self._manager.logger)
        self.logging_enabled.set(
            value=settings.get("logging_enabled", DEFAULT_LOG_ENABLED)
        )
        self.log_level.set(
            value=settings.get("log_level", DEFAULT_LOG_LEVEL)
        )
        self.address.set(
            value=settings.get("address", DEFAULT_ADDRESS)
        )
        self.port_number.set(
            value=settings.get("port_number", DEFAULT_PORT)
        )
        self.max_ws_connections.set(
            value=settings.get("max_ws_connections", DEFAULT_MAX_WS_CONNECTIONS)
        )
        self.max_reconnect_attempts.set(
            value=settings.get("max_reconnect_attempts", DEFAULT_MAX_RECONNECT_ATTEMPTS)
        )
        self.reconnect_base_delay.set(
            value=settings.get("reconnect_base_delay", DEFAULT_RECONNECT_BASE_DELAY)
        )
        self.gui_refresh_interval.set(
            value=settings.get("gui_refresh_interval", DEFAULT_GUI_REFRESH_INTERVAL)
        )


    def _save_settings_to_file(self) -> bool:
        """
        Serialize current settings to a file.
        """

        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.get_current_settings(), f, indent=4)
            return True
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            self._manager.logger.error("Failed to save settings to file: %s", e)
            return False


    def is_active(self):
        """
        Check if the settings window is active
        """
        return hasattr(self, '_window') and self._window.winfo_exists()


    def close_window(self) -> None:
        """
        Close window.
        """

        if self.is_active():
            self.on_close()


    def on_close(self):
        """
        On close handler
        """

        # Destroy the window to free Tk resources
        self._window.destroy()

        # Optionally delete the _window reference
        del self._window
