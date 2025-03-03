from PySide6.QtWidgets import (
    QMainWindow
)
from abc import abstractmethod

class IMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(IMainWindow, self).__init__(parent)
    @abstractmethod
    def show_folder_dialog(self, default_path) -> str: pass

    @abstractmethod
    def set_folder_path(self, path: str): pass

    @abstractmethod
    def get_folder_path(self) -> str: pass

    @abstractmethod
    def get_opacity_input(self) -> str: pass

    @abstractmethod
    def show_error(self, message: str) -> None: pass

    @abstractmethod
    def set_window_topmost(self, is_topmost: bool) -> None: pass