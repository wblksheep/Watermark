import logging
import os
import time
import queue
import threading
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from typing import List, Tuple, Iterable
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

# 线程安全的日志系统
class LogSystem:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._setup()
        return cls._instance

    @classmethod
    def _setup(cls):
        """线程安全的日志系统初始化"""
        cls.log_queue = queue.Queue(-1)  # 无界队列

        # 日志处理器配置
        file_handler = logging.FileHandler("watermark.log")
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(threadName)s - [%(levelname)s] - %(message)s"
        )
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # 启动后台日志监听线程
        cls.listener = QueueListener(
            cls.log_queue,
            file_handler,
            stream_handler,
            respect_handler_level=True
        )
        cls.listener.start()

    def shutdown(self):
        """安全关闭日志系统"""
        self.listener.stop()
        while not self.log_queue.empty():
            time.sleep(0.1)  # 等待队列处理完成

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        return (duration, result)
    return wrapper

def _default_stats():
    return {'count':0, 'total':0.0}

class BaseWatermarkProcessor:
    """优化后的多线程水印处理器"""

    _SUPPORTED_EXT = {'.jpg', '.jpeg', '.png'}

    def __init__(self, config):
        self._config = config
        self._timings = defaultdict(float)
        self._task_stats = defaultdict(_default_stats)
        self._log_system = LogSystem()
        self._log_queue = self._log_system.log_queue
        self._init_logger()

    def _init_logger(self):
        """初始化线程安全日志"""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.addHandler(QueueHandler(self._log_queue))
        self._logger.setLevel(logging.INFO)

    def _print_stats(self):
        """打印详细的耗时统计"""
        print("\n======== 性能分析报告 ========")
        print(f"[线程池初始化] {self._timings['pool_init']:.2f}s")
        print(f"[任务分发] {self._timings['task_distribute']:.2f}s")
        print(f"[结果收集] {self._timings['result_collect']:.2f}s")
        print(f"[总耗时] {self._timings['total']:.2f}s\n")

        print("=== 任务处理统计 ===")
        for task_type, stat in self._task_stats.items():
            avg = stat['total'] / stat['count'] if stat['count'] else 0
            print(f"{task_type}: 平均{avg:.2f}s | 总数{stat['total']:.2f}s | 次数{stat['count']}")

    def process_batch(self, input_dir: Path, output_dir: Path) -> List[Path]:
        """优化的批量处理方法"""
        output_dir.mkdir(parents=True, exist_ok=True)

        tasks = list(self._generate_tasks(input_dir, output_dir))
        if not tasks:
            self._logger.warning("未发现可处理文件")
            return []

        try:
            total_start = time.perf_counter()

            # 使用线程池替代进程池
            with ThreadPoolExecutor(
                max_workers=min(os.cpu_count() or 4, len(tasks)),
                initializer=self._init_worker
            ) as executor:
                # 计时开始
                self._timings['pool_init'] = time.perf_counter() - total_start

                # 任务分发
                task_start = time.perf_counter()
                futures = {
                    executor.submit(self._process_wrapper, task): task
                    for task in tasks
                }
                self._timings['task_distribute'] = time.perf_counter() - task_start

                # 结果收集
                collect_start = time.perf_counter()
                results = []
                for future in futures:
                    try:
                        success, output_path = future.result()
                        if success:
                            results.append(output_path)
                    except Exception as e:
                        self._logger.error(f"任务失败: {e}", exc_info=True)
                self._timings['result_collect'] = time.perf_counter() - collect_start

                return results
        finally:
            self._timings['total'] = time.perf_counter() - total_start
            self._print_stats()
            self._log_system.shutdown()

    def _generate_tasks(self, input_dir: Path, output_dir: Path) -> Iterable[Tuple[Path, Path]]:
        """任务生成器"""
        for entry in os.scandir(input_dir):
            if entry.is_file() and Path(entry).suffix.lower() in self._SUPPORTED_EXT:
                yield (Path(entry.path), output_dir / entry.name)

    @staticmethod
    def _init_worker():
        """工作线程初始化"""
        logger = logging.getLogger()
        logger.addHandler(QueueHandler(LogSystem().log_queue))
        logger.setLevel(logging.INFO)

    def _process_wrapper(self, task: Tuple[Path, Path]) -> Tuple[bool, Path]:
        """异常处理包装器"""
        try:
            start_time = time.perf_counter()

            # 实际处理逻辑
            self.process_single(task[0], task[1])

            cost = time.perf_counter() - start_time
            self._task_stats['process_single']['count'] += 1
            self._task_stats['process_single']['total'] += cost

            return (True, task)
        except Exception as e:
            self._logger.error(f"处理失败: {task} - {str(e)}", exc_info=True)
            return (False, task)

    def process_single(self, input_path: Path, output_path: Path):
        """具体处理逻辑（需子类实现）"""
        raise NotImplementedError

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def config(self):
        return self._config