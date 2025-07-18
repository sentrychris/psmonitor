from tkinter import Frame, Toplevel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app_manager import PSMonitorApp

class PSMonitorChildHandlerTemplate:
    """
    Handler template.
    """

    def __init__(
            self,
            window_title: str,
            manager: 'PSMonitorApp' = None
        ) -> None:
        """
        Initializes the handler.
        """

        self.window_title = window_title
        self.manager = manager


    def open_window(self) -> None:
        """
        Open graph window.
        """

        if hasattr(self, 'c_window') and self.c_window.winfo_exists():
            if not self.c_window.winfo_viewable():
                self.c_window.deiconify()
                # Re-register the child object if needed
                # if self.manager and self not in self.manager.active_child_handler_objects:
                #     self.manager.register_child_object(self)
            self.c_window.lift()
            return

        self.c_window = Toplevel(self.manager)
        self.c_window.title(self.window_title)
        self.c_window.geometry("450x500")
        self.c_window.resizable(False, False)

        # Register self to manager when window opens
        # if self.manager:
            # register method here

        self.c_window.protocol("WM_DELETE_WINDOW", self.on_close)


    def close_window(self) -> None:
        """
        Close window.
        """

        if hasattr(self, 'c_window') and self.c_window.winfo_exists():
            self.on_close()


    def on_close(self):
        """
        On close handler
        """
        # Destroy the window to free Tk resources
        self.c_window.destroy()

        # Optionally delete the c_window reference
        del self.c_window
