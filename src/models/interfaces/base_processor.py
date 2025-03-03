import logging
import os
import multiprocessing as mp
import logging
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from typing import List, Tuple, Iterable
from .interfaces import IWatermarkProcessor, IWatermarkConfig
import time
from collections import defaultdict

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

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        return (duration, result)
    return wrapper

def _default_stats():
    return {'count':0, 'total':0.0}

class BaseWatermarkProcessor(IWatermarkProcessor):
    """优化后的水印处理基类"""

    _SUPPORTED_EXT = {'.jpg', '.jpeg', '.png'}  # 预定义支持格式

    def __init__(self, config: IWatermarkConfig):
        self._config = config
        self._timings = defaultdict(float)
        self._task_stats = defaultdict(_default_stats)

    def _print_stats(self):
        """打印详细的耗时统计"""
        print("\n======== 性能分析报告 ========")
        print(f"[进程池初始化] {self._timings['pool_init']:.2f}s")
        print(f"[任务分发] {self._timings['task_distribute']:.2f}s")
        print(f"[结果收集] {self._timings['result_collect']:.2f}s")
        print(f"[资源回收] {self._timings['shutdown']:.2f}s")
        print(f"[总耗时] {self._timings['total']:.2f}s\n")

        print("=== 任务处理统计 ===")
        for task_type, stat in self._task_stats.items():
            avg = stat['total'] / stat['count'] if stat['count'] else 0
            print(f"{task_type}: 平均{avg:.2f}s | 总数{stat['total']:.2f}s | 次数{stat['count']}")

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
            total_start = time.perf_counter()

            # 进程池初始化计时
            pool_init_start = time.perf_counter()
            with mp.Pool(
                    processes=pool_size,
                    initializer=self._init_worker,
                    initargs=(log_system.log_queue,)
            ) as pool:
                self._timings['pool_init'] = time.perf_counter() - pool_init_start
                # 任务分发计时
                task_start = time.perf_counter()
                results = pool.imap_unordered(
                    self._process_wrapper,
                    tasks,
                    chunksize=10  # 优化内存使用
                )
                self._timings['task_distribute'] = time.perf_counter() - task_start
                # 结果收集计时
                collect_start = time.perf_counter()
                result = [
                    output_path
                    for success, output_path in results
                    if success
                ]
                self._timings['result_collect'] = time.perf_counter() - collect_start
                return result
        finally:
            # 资源回收计时
            shutdown_start = time.perf_counter()
            log_system.shutdown()
            self._timings['shutdown'] = time.perf_counter() - shutdown_start
            # 总耗时计算
            self._timings['total'] = time.perf_counter() - total_start
            self._print_stats()



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
            self.process_single(task[0], task[1])
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

    @property
    def config(self):
        return self._config

    def __del__(self):
        """安全关闭日志监听"""
        if hasattr(self, '_listener'):
            self._listener.stop()
