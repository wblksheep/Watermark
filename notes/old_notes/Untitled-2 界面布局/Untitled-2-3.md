增加一个按钮，控制界面是否始终在前

---- v3

在 PySide6 中，我们可以通过动态修改窗口的 `windowFlags` 来实现控制窗口是否始终在最前面的功能。以下是完整的代码示例，包含一个按钮用于切换窗口是否始终在最前面：

### 示例代码

```python
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
```

---

### 代码说明

1. **切换窗口始终在最前面**：

   - 使用 `self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)` 将窗口设置为始终在最前面。
   - 使用 `self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)` 取消窗口始终在最前面的设置。
   - 通过 `self.show()` 重新显示窗口以应用新的标志。

2. **按钮功能**：

   - `toggle_button` 用于切换窗口是否始终在最前面，并更新按钮文本。
   - `close_button` 用于关闭窗口。

3. **美化**：
   - 使用 `setStyleSheet` 为按钮设置样式，使其具有圆角和悬停效果。

---

### 运行效果

1. 窗口启动后，默认不始终在最前面。
2. 点击“窗口始终在前: 关闭”按钮，窗口会切换为始终在最前面，按钮文本变为“窗口始终在前: 开启”。
3. 再次点击按钮，窗口会取消始终在最前面的设置，按钮文本恢复为“窗口始终在前: 关闭”。
4. 点击“关闭窗口”按钮可以关闭窗口。

---

### 依赖安装

确保已安装 PySide6：

```bash
pip install PySide6
```

运行代码后，你将看到一个可以动态控制窗口是否始终在最前面的界面。可以根据需要进一步调整样式和功能。
