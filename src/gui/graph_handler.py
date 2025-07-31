"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: graph_handler.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 2.0.0.1011
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import tkinter as tk
from tkinter import ttk
from typing import Callable, TYPE_CHECKING

# Third party imports
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
# pylint: disable=wrong-import-position
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# pylint: enable=wrong-import-position

# Typing (type hints only, no runtime dependency)
if TYPE_CHECKING:
    from gui.app_manager import PSMonitorApp


class PSMonitorGraph:
    """
    Data graph.
    """

    def __init__(
            self,
            data_key: str,
            data_metric: str,
            data_callback: Callable[[], dict],
            y_label: str,
            window_title: str,
            handler: "PSMonitorAppGraphHandler" = None
        ) -> None:
        """
        Initializes the handler with initial data.
        """

        self._index = 0
        self._max_points = 60
        self._buffer_data = np.zeros(self._max_points)
        self._data_filled = False
        self._data_key = data_key
        self._data_metric = data_metric
        self._y_label = y_label
        self._label_suffix = "°C" if self._data_metric == "temp" else "%"

        self._window = None
        self._window_title = window_title

        self._g_fig = None    # matplotlib figure
        self._g_ax = None     # matplotlib graph
        self._g_canvas = None # matplotlib axis
        self._g_line = None   # matplotlib line


        self._handler = handler
        self._get_latest_data = data_callback


    def open_window(self) -> None:
        """
        Open graph window.
        """

        if hasattr(self, "_window") and self._window and self._window.winfo_exists():
            if not self._window.winfo_viewable():
                self._window.deiconify()
                # Re-register the graph if needed
                if self._handler and self not in self._handler.active_graphs:
                    self._handler.register_graph(self)
            self._window.lift()
            return

        self._window = tk.Toplevel(self._handler.manager)
        self._window.title(self._window_title)
        self._window.geometry("600x200")
        self._window.resizable(False, False)

        # Create border frame
        border_frame = ttk.Frame(self._window, borderwidth=2, relief="sunken")
        border_frame.pack(expand=True, fill="both", padx=3, pady=3)

        # Create matplotlib figure and axis
        self._g_fig = Figure(figsize=(5, 3), dpi=100)
        self._g_fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.05)

        self._g_ax = self._g_fig.add_subplot(111)
        self._g_ax.grid(axis="y", linewidth=0.5, alpha=0.7)
        self._g_ax.set_xticklabels([])
        self._g_ax.set_ylabel(self._y_label)
        self._g_ax.tick_params(axis="x", which="both", bottom=False, top=False)
        self._g_ax.tick_params(axis="y", which="major", labelsize=7)
        self._g_ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=20))
        self._g_ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=10))
        self._g_ax.set_ylim(0, 100)

        for spine in self._g_ax.spines.values():
            spine.set_alpha(0.3)

        self._g_line, = self._g_ax.plot([], [], "r-")

        # Create canvas in border frame
        self._g_canvas = FigureCanvasTkAgg(self._g_fig, master=border_frame)
        self._g_canvas.get_tk_widget().pack(expand=True, fill="both", padx=0, pady=0)
        self._g_canvas.draw()

        # Register self to graph handler when window opens
        if self._handler:
            self._handler.register_graph(self)

        self._window.protocol("WM_DELETE_WINDOW", self.on_close)


    def refresh_graph(self) -> None:
        """
        Loop the graph update using interval from the parent handler.
        """

        if not hasattr(self, "_window") or not self._window.winfo_exists():
            return  # Stop if window is closed

        curr_value = self._sample_data()
        self._update_plot()

        if curr_value is not None:
            try:
                title = f"{self._window_title} - ({curr_value:.1f} {self._label_suffix})"
                self._window.title(title)
            except Exception:
                pass


    def is_active(self):
        """
        Check if the graph is active
        """
        return hasattr(self, "_window") and self._window.winfo_exists()


    def close_window(self) -> None:
        """
        Close graph window.
        """

        if self.is_active():
            self.on_close()


    def on_close(self):
        """
        On close handler
        """
        # Destroy the window to free Tk resources
        self._window.destroy()

        # Explicitly clear matplotlib objects to free memory
        if hasattr(self, "_g_fig"):
            self._g_fig.clf()
            del self._g_fig
        if hasattr(self, "_g_ax"):
            del self._g_ax
        if hasattr(self, "_g_canvas"):
            self._g_canvas.get_tk_widget().destroy()
            del self._g_canvas
        if hasattr(self, "_g_line"):
            del self._g_line

        # Optionally delete the _window reference
        del self._window


    def _insert_buffer(self, temp) -> None:
        """
        Inserts a new data point value into the ring buffer.
        """

        self._buffer_data[self._index % self._max_points] = temp
        self._index += 1
        self._data_filled = self._data_filled or self._index >= self._max_points


    def _sample_data(self) -> float | None:
        """
        Sample the latest data and store it in the ring buffer.
        """

        if self._get_latest_data:
            try:
                data = self._get_latest_data()
                # metric = round(random.uniform(30, 50), 1)
                metric = data[self._data_key][self._data_metric]
                self._insert_buffer(metric)

                return float(metric)
            except (ValueError, TypeError, KeyError):
                return None

        return None


    def _update_plot(self) -> None:
        """
        Redraw the plot using the current contents of the ring buffer.
        """

        if self._index == 0:
            return  # no data yet

        # Slice actual data range
        if self._data_filled:
            offset = self._index % self._max_points
            y = np.roll(self._buffer_data, -offset)
            x = np.arange(self._index - self._max_points, self._index)
        else:
            y = self._buffer_data[:self._index]
            x = np.arange(self._index)

        if not np.array_equal(self._g_line.get_ydata(), y):
            self._g_line.set_data(x, y)
            if len(x) > 1 and x[0] != x[-1]:
                self._g_ax.set_xlim(x[0], x[-1])
            else:
                self._g_ax.set_xlim(0, self._max_points - 1)
            self._g_canvas.draw_idle()


class PSMonitorAppGraphHandler():
    """
    Graph handler.
    """

    def __init__(self, manager: "PSMonitorApp"):
        """
        Initialize the graph handler.
        """

        self.active_graphs: list[PSMonitorGraph] = []
        self.manager = manager


    def create_graph(self, key: str, metric: str, y_label: str, title: str) -> PSMonitorGraph:
        """
        Creates a new graph instance.
        """

        return PSMonitorGraph(
            data_key=key,
            data_metric=metric,
            data_callback=lambda: self.manager.data,
            y_label=y_label,
            window_title=title,
            handler=self
        )


    def register_graph(self, graph: PSMonitorGraph) -> None:
        """
        Register a new graph instance.
        """

        if graph not in self.active_graphs:
            self.active_graphs.append(graph)


    def unregister_graph(self, graph: PSMonitorGraph) -> None:
        """
        Unregister an existing graph instance.
        """

        if graph in self.active_graphs:
            self.active_graphs.remove(graph)


    def update_active_graphs(self) -> None:
        """
        Update active graphs.
        """

        for graph in self.active_graphs[:]:
            if graph.is_active():
                graph.refresh_graph()
            else:
                self.unregister_graph(graph)
