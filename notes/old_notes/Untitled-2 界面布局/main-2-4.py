import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("通过菜单控制窗口置顶示例")
        self.setGeometry(100, 100, 400, 300)

        # 创建菜单栏
        self.create_menu_bar()

    def create_menu_bar(self):
        # 创建菜单栏
        menu_bar = self.menuBar()

        # 创建“窗口”菜单
        window_menu = menu_bar.addMenu("窗口")

        # 创建“始终置顶”菜单项
        self.always_on_top_action = QAction("始终置顶", self)
        self.always_on_top_action.setCheckable(True)  # 设置为可勾选
        self.always_on_top_action.setChecked(False)   # 默认不勾选
        self.always_on_top_action.triggered.connect(self.toggle_always_on_top)
        window_menu.addAction(self.always_on_top_action)

        # 创建“关闭窗口”菜单项
        close_action = QAction("关闭窗口", self)
        close_action.triggered.connect(self.close)
        window_menu.addAction(close_action)

    def toggle_always_on_top(self):
        # 切换窗口是否始终在最前面
        if self.always_on_top_action.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.always_on_top_action.setText("取消始终置顶")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.always_on_top_action.setText("始终置顶")
        self.show()  # 重新显示窗口以应用新的标志

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())