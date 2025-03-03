import logging
import os
import multiprocessing as mp
import logging
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from typing import List, Tuple, Iterable
from .interfaces import IWatermarkProcessor, IWatermarkConfig

# 移除全局listener变量，改为类封装
class LogSystem:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls.manager = mp.Manager()
            cls.log_queue = cls.manager.Queue()
            file_handler = logging.FileHandler("watermark.log")
            stream_handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(processName)s - [%(levelname)s] - %(message)s")
            file_handler.setFormatter(formatter)
            stream_handler.setFormatter(formatter)
            cls.listener = QueueListener(
                cls.log_queue,
                file_handler,
                stream_handler
            )
            cls.listener.start()
        return cls._instance

    def __del__(self):
        if mp.current_process().name == 'MainProcess':
            if hasattr(self, 'listener'):
                try:
                    self.listener.stop()
                except Exception:  # 防止二次错误
                    pass
    def shutdown(self):
        """显式关闭方法"""
        self.listener.stop()
        self.manager.shutdown()


class BaseWatermarkProcessor(IWatermarkProcessor):
    """优化后的水印处理基类"""

    _SUPPORTED_EXT = {'.jpg', '.jpeg', '.png'}  # 预定义支持格式

    def __init__(self, config: IWatermarkConfig):
        self._config = config

    def process_batch(self, input_dir: Path, output_dir: Path) -> List[Path]:
        log_system = LogSystem()
        self._log_queue = log_system.log_queue
        """优化的批量处理方法"""
        output_dir.mkdir(parents=True, exist_ok=True)

        tasks = list(self._generate_tasks(input_dir, output_dir))
        if not tasks:
            self.logger.warning("未发现可处理文件")
            return []

        # 动态调整进程数
        pool_size = min(os.cpu_count() or 4, len(tasks))
        try:
            with mp.Pool(
                    processes=pool_size,
                    initializer=self._init_worker,
                    initargs=(log_system.log_queue,)
            ) as pool:
                results = pool.imap_unordered(
                    self._process_wrapper,
                    tasks,
                    chunksize=10  # 优化内存使用
                )
                result = [
                    output_path
                    for success, output_path in results
                    if success
                ]
        finally:
            log_system.shutdown()
            return result



    def _generate_tasks(self, input_dir: Path, output_dir: Path) -> Iterable[Tuple[Path, Path]]:
        """高效任务生成器"""
        for entry in os.scandir(input_dir):
            if entry.is_file() and Path(entry).suffix.lower() in self._SUPPORTED_EXT:
                yield (
                    Path(entry.path),
                    output_dir / entry.name
                )

    # @staticmethod
    # def _init_worker(log_queue: mp.Queue):
    #     """优化的进程初始化"""
    #     logger = logging.getLogger()
    #     logger.handlers = [QueueHandler(log_queue)]
    #     logger.setLevel(logging.INFO)
    def _init_worker(self, log_queue):
        """子进程日志初始化（每个子进程调用一次）"""
        # 获取当前进程的 logger
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        # 清除已有处理器，避免重复
        if self._logger.hasHandlers():
            self._logger.handlers.clear()

        # 添加队列处理器
        queue_handler = QueueHandler(log_queue)
        self._logger.addHandler(queue_handler)

    def _process_wrapper(self, task: Tuple[Path, Path]) -> Tuple[bool, Path]:
        """异常处理包装器"""
        try:
            self.process_single(task, task)
            return (True, task)
        except Exception as e:
            self.logger.error(f"处理失败: {task} - {str(e)}", exc_info=True)
            return (False, task)

    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
            self._logger.addHandler(QueueHandler(self._log_queue))
            self._logger.setLevel(logging.INFO)
        return self._logger

    def __del__(self):
        """安全关闭日志监听"""
        if hasattr(self, '_listener'):
            self._listener.stop()
