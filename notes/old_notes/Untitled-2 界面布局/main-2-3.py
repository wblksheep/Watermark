import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("控制窗口始终在前示例")
        self.setGeometry(100, 100, 400, 300)

        # 创建主窗口的中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建布局
        layout = QVBoxLayout()

        # 创建切换按钮
        self.toggle_button = QPushButton("窗口始终在前: 关闭")
        self.toggle_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 16px;
                background-color: #008CBA;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #007B9E;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_always_on_top)
        layout.addWidget(self.toggle_button)

        # 创建关闭按钮
        close_button = QPushButton("关闭窗口")
        close_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 16px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        # 设置布局
        central_widget.setLayout(layout)

    def toggle_always_on_top(self):
        # 切换窗口是否始终在最前面
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.toggle_button.setText("窗口始终在前: 关闭")
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.toggle_button.setText("窗口始终在前: 开启")
        self.show()  # 重新显示窗口以应用新的标志

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())