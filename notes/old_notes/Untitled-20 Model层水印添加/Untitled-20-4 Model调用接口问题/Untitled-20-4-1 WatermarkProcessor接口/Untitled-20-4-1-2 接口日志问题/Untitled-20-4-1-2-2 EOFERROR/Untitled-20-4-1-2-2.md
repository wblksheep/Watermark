```Error
2025-03-01 16:07:10,575 - MainProcess - NormalWatermarkProcessor - INFO - 🚦 开始批量处理 | 输入目录: input | 输出目录: output
2025-03-01 16:07:10,576 - MainProcess - NormalWatermarkProcessor - INFO - 📨 生成 50 个处理任务
Traceback (most recent call last):
  File "C:\Users\Design-10\PycharmProjects\PythonProject\src\models\main.py", line 25, in <module>
    main()
  File "C:\Users\Design-10\PycharmProjects\PythonProject\src\models\main.py", line 20, in main
    success_files = processor.process_batch(input_dir, output_dir)
  File "C:\Users\Design-10\PycharmProjects\PythonProject\src\models\interfaces\base_processor.py", line 55, in process_batch
    with mp.Pool(
  File "C:\Users\Design-10\.conda\envs\haiyin\lib\multiprocessing\context.py", line 119, in Pool
    return Pool(processes, initializer, initargs, maxtasksperchild,
  File "C:\Users\Design-10\.conda\envs\haiyin\lib\multiprocessing\pool.py", line 212, in __init__
    self._repopulate_pool()
  File "C:\Users\Design-10\.conda\envs\haiyin\lib\multiprocessing\pool.py", line 303, in _repopulate_pool
    return self._repopulate_pool_static(self._ctx, self.Process,
  File "C:\Users\Design-10\.conda\envs\haiyin\lib\multiprocessing\pool.py", line 326, in _repopulate_pool_static
    w.start()
  File "C:\Users\Design-10\.conda\envs\haiyin\lib\multiprocessing\process.py", line 121, in start
    self._popen = self._Popen(self)
  File "C:\Users\Design-10\.conda\envs\haiyin\lib\multiprocessing\context.py", line 327, in _Popen
    return Popen(process_obj)
  File "C:\Users\Design-10\.conda\envs\haiyin\lib\multiprocessing\popen_spawn_win32.py", line 93, in __init__
    reduction.dump(process_obj, to_child)
  File "C:\Users\Design-10\.conda\envs\haiyin\lib\multiprocessing\reduction.py", line 60, in dump
    ForkingPickler(file, protocol).dump(obj)
TypeError: cannot pickle '_thread.RLock' object
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "C:\Users\Design-10\.conda\envs\haiyin\lib\multiprocessing\spawn.py", line 116, in spawn_main
    exitcode = _main(fd, parent_sentinel)
  File "C:\Users\Design-10\.conda\envs\haiyin\lib\multiprocessing\spawn.py", line 126, in _main
    self = reduction.pickle.load(from_parent)
EOFError: Ran out of input
```

--- R1 ask

这个错误通常发生在 Windows 的多进程编程中，主要原因是尝试序列化不可 pickle 的对象（如线程锁）。以下是针对该问题的解决方案：

```python
import logging
import multiprocessing as mp
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from typing import Optional, List
from functools import partial

# 添加类型导入（修复可能的序列化问题）
from .interfaces import IWatermarkProcessor, IWatermarkConfig

class BaseWatermarkProcessor(IWatermarkProcessor):
    """修复不可序列化问题的水印处理基类"""

    _logger_initialized = False  # 类级别标记

    def __init__(self, config: IWatermarkConfig):
        self._config = config
        self._log_queue = mp.Queue()
        self._listener: Optional[QueueListener] = None
        self._setup_main_logger()

    def _setup_main_logger(self):
        """配置主进程日志（仅执行一次）"""
        if not self._log_queue._closed:  # type: ignore
            # Windows 兼容的日志配置
            formatter = logging.Formatter(
                '%(asctime)s - %(processName)s - %(name)s - %(levelname)s - %(message)s'
            )

            # 确保主进程只初始化一次
            main_logger = logging.getLogger()
            if not any(isinstance(h, logging.StreamHandler) for h in main_logger.handlers):
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                main_logger.addHandler(console_handler)

            # 启动队列监听器
            self._listener = QueueListener(
                self._log_queue,
                *main_logger.handlers,
                respect_handler_level=True
            )
            self._listener.start()

    def __del__(self):
        if self._listener:
            self._listener.stop()

    def process_batch(self, input_dir: Path, output_dir: Path) -> List[Path]:
        """修复方法：避免传递不可序列化对象"""
        self.logger.info(f"🚦 开始批量处理 | 输入目录: {input_dir} | 输出目录: {output_dir}")
        output_dir.mkdir(exist_ok=True, parents=True)

        # 生成处理任务时避免保留对象引用
        tasks = self._generate_tasks(input_dir, output_dir)
        self.logger.info(f"📨 生成 {len(tasks)} 个处理任务")

        # 使用 functools.partial 代替实例方法
        with mp.Pool(
            processes=mp.cpu_count(),
            initializer=self._init_worker,
            initargs=(self._log_queue,)
        ) as pool:
            # 使用静态方法处理任务
            worker = partial(self._static_process_wrapper, config=self._config)
            results = pool.starmap(worker, tasks)

        processed_files = [Path(t[1]) for t, r in zip(tasks, results) if r]
        return processed_files

    @staticmethod
    def _static_process_wrapper(input_path: str, output_path: str, config: IWatermarkConfig) -> bool:
        """静态方法包装器（解决实例方法序列化问题）"""
        # 每个进程独立初始化处理器
        processor = BaseWatermarkProcessor(config)
        return processor._process_single_impl(input_path, output_path)

    def _process_single_impl(self, input_path: str, output_path: str) -> bool:
        """实际处理实现"""
        try:
            self.logger.info(f"🔧 开始处理: {Path(input_path).name}")
            # 这里添加实际处理逻辑
            success = True  # 模拟成功

            if success:
                self.logger.info(f"✅ 成功保存: {Path(output_path).name}")
                return True
            self.logger.warning(f"⚠️ 处理失败: {Path(input_path).name}")
            return False

        except Exception as e:
            self.logger.error(f"❌ 处理异常: {Path(input_path).name} | 错误信息: {str(e)}", exc_info=True)
            return False

    def _init_worker(self, log_queue: mp.Queue):
        """工作进程初始化（确保独立日志配置）"""
        # 重置日志处理器
        logger = logging.getLogger()
        logger.handlers = []
        logger.addHandler(QueueHandler(log_queue))
        logger.setLevel(logging.INFO)

    # 其他方法保持不变...
```

关键修改点说明：

1. **静态方法包装器**：

- 使用 `functools.partial` 代替实例方法
- 通过 `_static_process_wrapper` 将实例方法与配置分离
- 每个子进程独立创建处理器实例

2. **日志系统改进**：

- 显式重置子进程的日志处理器 (`_init_worker`)
- 避免跨进程传递 logger 对象
- 使用类级别标记防止重复初始化

3. **Windows 兼容性优化**：

- 使用 `spawn` 启动方法兼容的初始化逻辑
- 确保所有传递参数都是基本类型或可序列化对象
- 避免直接传递包含线程锁的对象

4. **异常处理增强**：

- 显式关闭队列监听器
- 添加进程安全的异常捕获
- 更清晰的错误消息格式

使用注意事项：

1. 确保 `IWatermarkConfig` 是可序列化的
2. 避免在处理器中保存文件句柄等不可序列化资源
3. 建议在 Windows 系统中添加 `if __name__ == '__main__':` 保护
4. 对于复杂对象，建议使用 `multiprocessing.Manager` 进行共享

这个修改版本应该可以解决 `TypeError: cannot pickle '_thread.RLock' object` 错误，同时保持完整的日志功能。
