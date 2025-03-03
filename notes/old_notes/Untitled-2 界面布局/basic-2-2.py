import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("窗口始终在前示例")
        self.setGeometry(100, 100, 400, 300)

        # 设置窗口始终在最前面
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # 添加一个按钮
        button = QPushButton("关闭窗口", self)
        button.clicked.connect(self.close)
        button.setGeometry(150, 100, 100, 50)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())