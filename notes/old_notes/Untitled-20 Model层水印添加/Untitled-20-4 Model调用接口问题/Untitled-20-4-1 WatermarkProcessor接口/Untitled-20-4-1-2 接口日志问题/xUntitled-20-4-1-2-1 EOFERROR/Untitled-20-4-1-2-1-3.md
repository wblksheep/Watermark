```error
Traceback (most recent call last):
  File "C:\Users\Design-10\PycharmProjects\PythonProject\src\models\main.py", line 4, in <module>
    from src.models.interfaces.impl.normal_processor import NormalWatermarkProcessor
  File "C:\Users\Design-10\PycharmProjects\PythonProject\src\models\interfaces\impl\normal_processor.py", line 6, in <module>
    from src.models.interfaces.base_processor import BaseWatermarkProcessor
  File "C:\Users\Design-10\PycharmProjects\PythonProject\src\models\interfaces\base_processor.py", line 8, in <module>
    from .impl.normal_processor import NormalWatermarkProcessor
ImportError: cannot import name 'NormalWatermarkProcessor' from partially initialized module 'src.models.interfaces.impl.normal_processor' (most likely due to a circular import) (C:\Users\Design-10\PycharmProjects\PythonProject\src\models\interfaces\impl\normal_processor.py)
```

---- R1

这个循环导入问题需要通过代码结构调整来解决。以下是完整的解决方案：

```python
# 文件结构建议
src/
├── models/
│   ├── interfaces/
│   │   ├── __init__.py          # 导出基类
│   │   ├── base_processor.py    # 仅包含基类
│   │   └── impl/
│   │       ├── __init__.py      # 导出具体实现
│   │       └── normal_processor.py # 具体实现类
│   └── main.py
```

1. **base_processor.py** (仅包含抽象基类)

```python
from __future__ import annotations
import logging
import multiprocessing as mp
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from typing import Optional, List, Dict, Type

class BaseWatermarkProcessor:
    """完全独立的基类，不依赖任何子类"""

    def __init__(self, config: Dict):
        self._config = config
        self._manager = mp.Manager()
        self._log_queue = self._manager.Queue()
        self._logger = None
        self._setup_log_system()

    def _setup_log_system(self):
        if mp.current_process().name == 'MainProcess':
            formatter = logging.Formatter(
                '%(asctime)s - %(processName)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            self._listener = QueueListener(
                self._log_queue,
                console_handler,
                respect_handler_level=True
            )
            self._listener.start()

    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            logger = logging.getLogger(self.__class__.__name__)
            logger.addHandler(QueueHandler(self._log_queue))
            logger.setLevel(logging.INFO)
            self._logger = logger
        return self._logger

    @classmethod
    def create(cls: Type[BaseWatermarkProcessor], config: Dict) -> BaseWatermarkProcessor:
        """工厂方法使用字符串类型引用"""
        return cls(config)

    def process_batch(self, input_dir: Path, output_dir: Path) -> List[Path]:
        raise NotImplementedError
```

2. **normal_processor.py** (具体实现类)

```python
from pathlib import Path
from typing import List
from ...interfaces.base_processor import BaseWatermarkProcessor  # 使用绝对导入

class NormalWatermarkProcessor(BaseWatermarkProcessor):
    """独立的具体实现类"""

    def __init__(self, config: Dict):
        super().__init__(config)
        # 具体初始化逻辑

    def process_batch(self, input_dir: Path, output_dir: Path) -> List[Path]:
        # 具体实现逻辑
        return []
```

3. **main.py** (主程序)

```python
from pathlib import Path
from models.interfaces.impl.normal_processor import NormalWatermarkProcessor

def main():
    config = {"watermark": "logo.png"}  # 示例配置
    processor = NormalWatermarkProcessor(config)
    success_files = processor.process_batch(
        Path("input"),
        Path("output")
    )

if __name__ == "__main__":
    main()
```

关键修改点说明：

1. **消除循环依赖**：

- 基类 `BaseWatermarkProcessor` 完全独立，不导入任何子类
- 子类通过绝对路径导入基类
- 使用 `from __future__ import annotations` 实现延迟类型注解

2. **导入路径修正**：

```python
# normal_processor.py 使用清晰的导入路径
from ...interfaces.base_processor import BaseWatermarkProcessor
```

3. **工厂方法模式**：

```python
# 在基类中使用类型变量实现灵活创建
@classmethod
def create(cls: Type[BaseWatermarkProcessor], config: Dict) -> BaseWatermarkProcessor:
    return cls(config)
```

4. **配置传递优化**：

- 统一使用字典进行配置传递
- 具体类自行处理配置解析

验证方法：

```bash
# 在项目根目录执行
python -m src.models.main
```

典型目录结构验证：

```
src/
├── __init__.py
└── models/
    ├── __init__.py
    ├── main.py
    └── interfaces/
        ├── __init__.py          # 导出基类
        ├── base_processor.py
        └── impl/
            ├── __init__.py      # 导出具体实现类
            └── normal_processor.py
```

附加建议：

1. 使用 `isort` 自动排序导入

```bash
pip install isort
isort .
```

2. 使用模块级 `__init__.py` 控制导出：

```python
# interfaces/__init__.py
from .base_processor import BaseWatermarkProcessor
__all__ = ['BaseWatermarkProcessor']

# interfaces/impl/__init__.py
from .normal_processor import NormalWatermarkProcessor
__all__ = ['NormalWatermarkProcessor']
```

3. 类型注解最佳实践：

```python
def process(self) -> List[Path]:  # 使用标准类型
    ...

def factory(config: Dict) -> "NormalWatermarkProcessor":  # 需要前向引用时使用字符串
    ...
```

该方案通过以下方式彻底解决循环导入问题：

- 严格分离抽象与实现
- 使用明确的绝对导入路径
- 延迟类型注解评估
- 合理的模块导出控制
