import matplotlib
import numpy as np

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Frame, Toplevel
from typing import Callable

class CPUTempGraph:
    """
    CPU temperature graph handler.
    """

    def __init__(self, update_interval: int, data_callback: Callable[[], dict]) -> None:
        """
        Initializes the handler with initial data.
        
        Args:
            update_interval (int): The graph update interval.
            data_callback (callable): The callback to get latest data
        """

        self.max_points = 60
        self.cpu_temp_data = np.zeros(self.max_points)
        self.index = 0
        self.data_filled = False
        self.get_latest_data = data_callback
        self.update_interval = update_interval


    def open_window(self, parent) -> None:
        """
        Open CPU Graph window.
        """

        if hasattr(self, 'cpu_graph_window') and self.cpu_graph_window.winfo_exists():
            # If window exists but is withdrawn (hidden), deiconify to show it again
            if not self.cpu_graph_window.winfo_viewable():
                self.cpu_graph_window.deiconify()
            self.cpu_graph_window.lift()
            return

        self.cpu_graph_window = Toplevel(parent)
        self.cpu_graph_window.title("CPU Temperature Graph")
        self.cpu_graph_window.geometry("600x200")
        self.cpu_graph_window.resizable(False, False)
        self.cpu_graph_window.protocol("WM_DELETE_WINDOW", self.cpu_graph_window.withdraw)  # Hide on close

        # Create border frame
        border_frame = Frame(self.cpu_graph_window, borderwidth=2, relief="sunken")
        border_frame.pack(expand=True, fill='both', padx=3, pady=3)

        # Create matplotlib figure and axis
        self.cpu_fig = Figure(figsize=(5, 3), dpi=100)
        self.cpu_fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.05)

        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_ax.grid(axis='y', linewidth=0.5, alpha=0.7)
        self.cpu_ax.set_xticklabels([])
        self.cpu_ax.set_ylabel("CPU Temp. (C°)")
        self.cpu_ax.tick_params(axis='x', which='both', bottom=False, top=False)
        self.cpu_ax.tick_params(axis='y', which='major', labelsize=7)
        self.cpu_ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=20))
        self.cpu_ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=10))
        self.cpu_ax.set_ylim(0, 100)

        for spine in self.cpu_ax.spines.values():
            spine.set_alpha(0.3)
    
        self.cpu_line, = self.cpu_ax.plot([], [], 'r-')

        # Create canvas in border frame
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, master=border_frame)
        self.cpu_canvas.get_tk_widget().pack(expand=True, fill='both', padx=0, pady=0)
        self.cpu_canvas.draw()

        self.update_graph()


    def close_window(self) -> None:
        """
        Close CPU temperature graph window.
        """

        if hasattr(self, 'cpu_graph_window') and self.cpu_graph_window.winfo_exists():
            self.cpu_graph_window.destroy()


    def insert_buffer(self, temp) -> None:
        """
        Inserts a new CPU temperature value into the ring buffer.
        """

        self.cpu_temp_data[self.index % self.max_points] = temp
        self.index += 1
        self.data_filled = self.data_filled or self.index >= self.max_points


    def sample_data(self) -> None:
        """
        Sample the latest CPU temperature and store it in the ring buffer.
        """

        if self.get_latest_data:
            try:
                data = self.get_latest_data()
                # cpu_temp = round(random.uniform(30, 50), 1)
                cpu_temp = data["cpu"]["temp"]
                self.insert_buffer(cpu_temp)
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
            y = np.roll(self.cpu_temp_data, -offset)
            x = np.arange(self.index - self.max_points, self.index)
        else:
            y = self.cpu_temp_data[:self.index]
            x = np.arange(self.index)

        if not np.array_equal(self.cpu_line.get_ydata(), y):
            self.cpu_line.set_data(x, y)
            if len(x) > 1 and x[0] != x[-1]:
                self.cpu_ax.set_xlim(x[0], x[-1])
            else:
                self.cpu_ax.set_xlim(0, self.max_points - 1)
            self.cpu_canvas.draw_idle()


    def update_graph(self) -> None:
        """
        Loop the CPU temp graph update using interval from the parent handler.
        """

        if not hasattr(self, 'cpu_graph_window') or not self.cpu_graph_window.winfo_exists():
            return  # Stop if window is closed

        self.sample_data()
        self.update_plot()

        self.cpu_graph_window.after(self.update_interval, self.update_graph)