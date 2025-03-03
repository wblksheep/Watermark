需要点击菜单开启是否始终置顶

-------- v3

为了实现通过菜单项控制窗口是否始终置顶的功能，我们可以在 PySide6 中使用 `QMenu` 和 `QAction` 来创建一个菜单项，并通过点击菜单项来切换窗口的置顶状态。以下是完整的代码示例：

### 示例代码

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction
from PySide6.QtCore import Qt

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
```

---

### 代码说明

1. **菜单栏和菜单项**：

   - 创建了一个“窗口”菜单，包含两个菜单项：“始终置顶”和“关闭窗口”。
   - `self.always_on_top_action` 是一个可勾选的 `QAction`，用于控制窗口是否始终置顶。

2. **切换窗口置顶状态**：

   - 当用户点击“始终置顶”菜单项时，`toggle_always_on_top` 方法会被调用。
   - 如果菜单项被勾选，窗口会设置为始终在最前面，并将菜单项文本更新为“取消始终置顶”。
   - 如果菜单项未被勾选，窗口会取消始终在最前面的设置，并将菜单项文本恢复为“始终置顶”。

3. **重新显示窗口**：
   - 修改 `windowFlags` 后，必须调用 `self.show()` 重新显示窗口以应用新的标志。

---

### 运行效果

1. 窗口启动后，默认不始终置顶。
2. 点击“窗口”菜单，选择“始终置顶”菜单项，窗口会切换为始终在最前面，菜单项文本变为“取消始终置顶”。
3. 再次点击“取消始终置顶”菜单项，窗口会取消始终置顶的设置，菜单项文本恢复为“始终置顶”。
4. 点击“关闭窗口”菜单项可以关闭窗口。

---

### 依赖安装

确保已安装 PySide6：

```bash
pip install PySide6
```

运行代码后，你将看到一个可以通过菜单控制窗口是否始终置顶的界面。可以根据需要进一步调整样式和功能。
