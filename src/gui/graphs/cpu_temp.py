import matplotlib
import random
import time

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Frame, Toplevel

class CPUTempGraph:
    """
    CPU Temp Graph Handler for the GUI.
    """

    def __init__(self):
        self.get_latest_data = None  # will be assigned later

    def open_window(self, parent):
        """
        Open CPU Graph window.
        """

        if hasattr(self, 'cpu_graph_window') and self.cpu_graph_window.winfo_exists():
            self.cpu_graph_window.lift()
            return

        self.cpu_graph_window = Toplevel(parent)
        self.cpu_graph_window.title("CPU Temperature Graph")
        self.cpu_graph_window.geometry("600x300")
        self.cpu_graph_window.protocol("WM_DELETE_WINDOW", self.cpu_graph_window.withdraw)  # Hide on close

        # Create border frame
        border_frame = Frame(self.cpu_graph_window, borderwidth=2, relief="sunken")
        border_frame.pack(expand=True, fill='both', padx=3, pady=3)

        # Create matplotlib figure and axis
        self.cpu_fig = Figure(figsize=(5, 3), dpi=100)
        self.cpu_fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.05)
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_ax.set_ylabel("CPU Temp. (C°)")
        self.cpu_ax.set_xticklabels([])
        self.cpu_ax.tick_params(axis='y', which='major', labelsize=7)
        self.cpu_ax.tick_params(axis='x', which='both', bottom=False, top=False)
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=20))
        self.cpu_ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=10))
        for spine in self.cpu_ax.spines.values():
            spine.set_alpha(0.3)
        self.cpu_ax.grid(True, linewidth=0.5, alpha=0.7)
        self.cpu_line, = self.cpu_ax.plot([], [], 'r-')

        # Create canvas in border frame
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, master=border_frame)
        self.cpu_canvas.get_tk_widget().pack(expand=True, fill='both', padx=0, pady=0)
        self.cpu_canvas.draw()

        # Initialize data buffers
        self.cpu_temp_data = []
        self.cpu_temp_times = []

        self.cpu_graph_start_time = time.time()
        self.update_graph_loop()


    def close_window(self):
        """
        Close CPU Graph window.
        """

        if hasattr(self, 'cpu_graph_window') and self.cpu_graph_window.winfo_exists():
            self.cpu_graph_window.destroy()


    def update_graph_loop(self):
        """
        Looped CPU temp graph update.
        """

        if not hasattr(self, 'cpu_graph_window') or not self.cpu_graph_window.winfo_exists():
            # Window closed, stop updates
            return

        try:
            if self.get_latest_data:
                data = self.get_latest_data()
                # cpu_temp = float(data['cpu']['temp'])
                cpu_temp = round(random.uniform(30, 50), 1)
                self.update_graph(cpu_temp)
        except (ValueError, TypeError, KeyError):
            pass

        # Repeat after 1 second
        self.cpu_graph_window.after(1000, self.update_graph_loop)


    def update_graph(self, new_temp):
        """
        Update CPU temp graph.
        """

        current_time = time.time()
        elapsed = current_time - self.cpu_graph_start_time

        self.cpu_temp_times.append(elapsed)
        self.cpu_temp_data.append(new_temp)

        max_points = 60
        if len(self.cpu_temp_data) > max_points:
            self.cpu_temp_data = self.cpu_temp_data[-max_points:]
            self.cpu_temp_times = self.cpu_temp_times[-max_points:]

        self.cpu_line.set_data(self.cpu_temp_times, self.cpu_temp_data)

        # Set x limits to match the actual data range
        min_x = self.cpu_temp_times[0] if self.cpu_temp_times else 0
        max_x = self.cpu_temp_times[-1] if self.cpu_temp_times else 60

        # Provide some margin for aesthetics
        if len(self.cpu_temp_times) > 1:
            min_x = self.cpu_temp_times[0]
            max_x = self.cpu_temp_times[-1]
            self.cpu_ax.set_xlim(min_x, max_x)
        else:
            # Set default x range (e.g. 0–60 seconds)
            self.cpu_ax.set_xlim(0, 60)

        self.cpu_canvas.draw_idle()