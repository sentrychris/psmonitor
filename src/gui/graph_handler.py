import matplotlib
import numpy as np

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Frame, Toplevel
from typing import Callable

class PSMonitorGraph:
    """
    Data graph handler.
    """

    def __init__(self, update_interval: int, data_key: str, data_metric: str,
            data_callback: Callable[[], dict], y_label: str, window_title: str,
            manager = None) -> None:
        """
        Initializes the handler with initial data.
        """

        self.index = 0
        self.max_points = 60
        self.buffer_data = np.zeros(self.max_points)
        self.data_filled = False
        self.data_key = data_key
        self.data_metric = data_metric
        self.y_label = y_label

        self.manager = manager

        self.window_title = window_title
        self.get_latest_data = data_callback
        self.update_interval = update_interval


    def open_window(self) -> None:
        """
        Open graph window.
        """

        if hasattr(self, 'g_window') and self.g_window.winfo_exists():
            if not self.g_window.winfo_viewable():
                self.g_window.deiconify()
                # Re-register the graph if needed
                if self.manager and self not in self.manager.active_graphs:
                    self.manager.register_graph(self)
            self.g_window.lift()
            return

        self.g_window = Toplevel(self.manager)
        self.g_window.title(self.window_title)
        self.g_window.geometry("600x200")
        self.g_window.resizable(False, False)

        # Create border frame
        border_frame = Frame(self.g_window, borderwidth=2, relief="sunken")
        border_frame.pack(expand=True, fill='both', padx=3, pady=3)

        # Create matplotlib figure and axis
        self.g_fig = Figure(figsize=(5, 3), dpi=100)
        self.g_fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.05)

        self.g_ax = self.g_fig.add_subplot(111)
        self.g_ax.grid(axis='y', linewidth=0.5, alpha=0.7)
        self.g_ax.set_xticklabels([])
        self.g_ax.set_ylabel(self.y_label)
        self.g_ax.tick_params(axis='x', which='both', bottom=False, top=False)
        self.g_ax.tick_params(axis='y', which='major', labelsize=7)
        self.g_ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=20))
        self.g_ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=10))
        self.g_ax.set_ylim(0, 100)

        for spine in self.g_ax.spines.values():
            spine.set_alpha(0.3)
    
        self.g_line, = self.g_ax.plot([], [], 'r-')

        # Create canvas in border frame
        self.g_canvas = FigureCanvasTkAgg(self.g_fig, master=border_frame)
        self.g_canvas.get_tk_widget().pack(expand=True, fill='both', padx=0, pady=0)
        self.g_canvas.draw()

        # Register self to manager when window opens
        if self.manager:
            self.manager.register_graph(self)
        
        def on_close():
            if self.manager:
                self.manager.unregister_graph(self)
            self.g_window.withdraw()

        self.g_window.protocol("WM_DELETE_WINDOW", on_close)


    def close_window(self) -> None:
        """
        Close graph window.
        """

        if hasattr(self, 'g_window') and self.g_window.winfo_exists():
            self.g_window.destroy()


    def insert_buffer(self, temp) -> None:
        """
        Inserts a new data point value into the ring buffer.
        """

        self.buffer_data[self.index % self.max_points] = temp
        self.index += 1
        self.data_filled = self.data_filled or self.index >= self.max_points


    def sample_data(self) -> None:
        """
        Sample the latest data and store it in the ring buffer.
        """

        if self.get_latest_data:
            try:
                data = self.get_latest_data()
                # metric = round(random.uniform(30, 50), 1)
                metric = data[self.data_key][self.data_metric]
                self.insert_buffer(metric)
            except (ValueError, TypeError, KeyError):
                pass


    def update_plot(self) -> None:
        """
        Redraw the plot using the current contents of the ring buffer.
        """

        if self.index == 0:
            return  # no data yet

        # Slice actual data range
        if self.data_filled:
            offset = self.index % self.max_points
            y = np.roll(self.buffer_data, -offset)
            x = np.arange(self.index - self.max_points, self.index)
        else:
            y = self.buffer_data[:self.index]
            x = np.arange(self.index)

        if not np.array_equal(self.g_line.get_ydata(), y):
            self.g_line.set_data(x, y)
            if len(x) > 1 and x[0] != x[-1]:
                self.g_ax.set_xlim(x[0], x[-1])
            else:
                self.g_ax.set_xlim(0, self.max_points - 1)
            self.g_canvas.draw_idle()


    def refresh_graph(self) -> None:
        """
        Loop the graph update using interval from the parent handler.
        """

        if not hasattr(self, 'g_window') or not self.g_window.winfo_exists():
            return  # Stop if window is closed

        self.sample_data()
        self.update_plot()