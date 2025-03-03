我如何导入本地一个名为 basic-2.py 的文件中的某个函数？

--- v3
要在 Python 中导入本地文件（如 `basic-2.py`）中的某个函数，可以使用 `import` 语句或 `from ... import ...` 语句。以下是具体步骤：

---

### 1. **确保文件在同一目录下**

假设你的当前脚本和 `basic-2.py` 文件在同一个目录下，例如：

```
project/
├── main.py
└── basic-2.py
```

---

### 2. **导入整个文件**

如果 `basic-2.py` 文件中有一个函数 `my_function`，你可以这样导入：

```python
import basic-2  # 导入整个文件

# 调用函数
basic-2.my_function()
```

注意：文件名 `basic-2.py` 中的 `-` 会导致语法错误，因为 Python 模块名不能包含 `-`。你需要将文件名改为 `basic_2.py`（用下划线代替连字符）。

---

### 3. **导入特定函数**

如果你只想导入 `basic_2.py` 文件中的某个函数，可以使用 `from ... import ...` 语法：

```python
from basic_2 import my_function  # 导入特定函数

# 直接调用函数
my_function()
```

---

### 4. **如果文件不在同一目录下**

如果 `basic_2.py` 文件不在当前目录下，你需要确保 Python 能够找到它。可以通过以下方法实现：

#### **方法 1：修改 `sys.path`**

在导入之前，将文件所在目录添加到 `sys.path` 中：

```python
import sys
sys.path.append("/path/to/directory")  # 添加文件所在目录

from basic_2 import my_function  # 导入函数
my_function()
```

#### **方法 2：使用相对导入（适用于包结构）**

如果 `basic_2.py` 文件在一个子目录中，可以使用相对导入。例如：

```
project/
├── main.py
└── utils/
    └── basic_2.py
```

在 `main.py` 中：

```python
from utils.basic_2 import my_function  # 从子目录导入
my_function()
```

---

### 5. **示例代码**

假设 `basic_2.py` 文件内容如下：

```python
# basic_2.py
def my_function():
    print("Hello from my_function!")
```

在 `main.py` 中导入并调用：

```python
from basic_2 import my_function  # 导入函数

my_function()  # 调用函数
```

---

### 6. **注意事项**

- 确保文件名和函数名拼写正确。
- 如果文件名包含特殊字符（如 `-`），需要重命名文件（如改为 `basic_2.py`）。
- 如果文件路径复杂，建议使用 `sys.path` 或相对导入。

通过以上方法，你可以成功导入本地文件中的函数并调用它。
