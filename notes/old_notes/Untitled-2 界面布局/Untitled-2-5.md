如何获取该对象的元素？

```python
        # 创建下拉菜单
        self.combo_box = QComboBox()
        self.combo_box.addItems(["选项 1", "选项 2", "选项 3"])
        self.combo_box.setStyleSheet("""
            QComboBox {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right top;
                width: 20px;
                border-left: 1px solid #ccc;
            }
            QComboBox::down-arrow {
                image: url(none);
            }
        """)
        layout.addWidget(self.combo_box)
```

---- v3

要获取 `QComboBox` 对象中的元素（即下拉菜单中的选项），你可以使用 `QComboBox` 提供的方法。以下是一些常用的方法：

1. **获取当前选中的文本**：

   ```python
   current_text = self.combo_box.currentText()
   print(current_text)
   ```

2. **获取当前选中的索引**：

   ```python
   current_index = self.combo_box.currentIndex()
   print(current_index)
   ```

3. **获取所有选项的文本**：

   ```python
   for i in range(self.combo_box.count()):
       item_text = self.combo_box.itemText(i)
       print(item_text)
   ```

4. **获取所有选项的索引和文本**：

   ```python
   for i in range(self.combo_box.count()):
       item_text = self.combo_box.itemText(i)
       print(f"Index: {i}, Text: {item_text}")
   ```

5. **获取指定索引的文本**：

   ```python
   index = 1  # 例如获取索引为1的选项
   item_text = self.combo_box.itemText(index)
   print(item_text)
   ```

6. **获取所有选项的列表**：
   ```python
   items = [self.combo_box.itemText(i) for i in range(self.combo_box.count())]
   print(items)
   ```

### 示例代码

以下是一个完整的示例，展示如何获取 `QComboBox` 中的元素：

```python
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 创建下拉菜单
        self.combo_box = QComboBox()
        self.combo_box.addItems(["选项 1", "选项 2", "选项 3"])
        layout.addWidget(self.combo_box)

        self.setLayout(layout)

        # 获取当前选中的文本
        current_text = self.combo_box.currentText()
        print(f"当前选中的文本: {current_text}")

        # 获取所有选项的文本
        for i in range(self.combo_box.count()):
            item_text = self.combo_box.itemText(i)
            print(f"选项 {i}: {item_text}")

if __name__ == '__main__':
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec_()
```

运行这个代码后，你会看到控制台输出当前选中的文本以及所有选项的文本。
