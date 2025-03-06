import logging
import os
import sys
import time
import queue
import threading
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from typing import List, Tuple, Iterable, runtime_checkable, Protocol, TypeVar, Generic
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

from pydantic import ValidationError, BaseModel


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
        # 增强日志格式（增加毫秒精度）
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d - %(threadName)-18s - [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
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
        # cls.listener_thread = threading.Thread(target=cls.listener.start)

    # def start(self):
    #     self.listener_thread.start()

    def shutdown(self):
        """安全关闭日志系统"""
        self.listener.stop()
        # self.listener_thread.join()  # 等待监听线程处理完成并终止
        # # 强制清空队列（可选）
        # while not self.log_queue.empty():
        #     try:
        #         self.log_queue.get_nowait()
        #     except queue.Empty:
        #         break

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        return (duration, result)
    return wrapper

def _default_stats():
    return {'count':0, 'total':0.0}

class ProcessorParams(BaseModel):
    """参数基类（定义公共字段）"""
    opacity: float = 0.8
    output_dir: Path

# 泛型参数约束
T = TypeVar("T", bound=ProcessorParams)

class BaseWatermarkProcessor(Generic[T]):
    """优化后的多线程水印处理器（日志增强版）"""

    _SUPPORTED_EXT = {'.jpg', '.jpeg', '.png'}

    def __init__(self, config):
        self._config = config
        self._timings = defaultdict(float)
        self._task_stats = defaultdict(_default_stats)
        self._log_system = LogSystem()
        self._log_queue = self._log_system.log_queue
        self._init_logger()
        self.default_params = self._parse_config(config)

    def _init_logger(self):
        """增强日志初始化"""
        self._logger = logging.getLogger(f"{self.__class__.__name__}.{id(self)}")
        self._logger.addHandler(QueueHandler(self._log_queue))
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False  # 避免重复记录

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

    def process_batch(self, input_dir: Path, output_dir: Path, **kwargs) -> List[Path]:
        try:
            final_params = self._validate_params(
                params = ProcessorParams(
                    **{**self.default_params, **kwargs},
                    output_dir=output_dir
                )
            )
        except ValidationError as e:
            self.logger.exception(e)
            raise ValueError(f"参数校验失败: {e.errors()}")
        """添加批处理各阶段日志"""
        self._logger.info(f"开始批处理任务 | 输入目录: {input_dir} | 输出目录: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
        tasks = list(self._generate_tasks(input_dir, output_dir))
        if not tasks:
            self._logger.warning("未发现可处理文件")
            return []

        try:
            # 生成任务阶段日志
            task_start = time.perf_counter()
            tasks = list(self._generate_tasks(input_dir, output_dir))
            gen_time = time.perf_counter() - task_start
            self._logger.info(
                f"扫描到 {len(tasks)} 个待处理文件 | "
                f"耗时: {gen_time:.2f}s | "
                f"跳过文件: {self._scan_skipped} 个"
            )
            # 线程池配置日志
            max_workers = min(os.cpu_count() or 4, len(tasks))
            self._logger.info(
                f"🛠初始化线程池 | 最大工作线程: {max_workers} | "
                f"总任务数: {len(tasks)} | "
                f"预计并发度: {min(max_workers, len(tasks))}"
            )
            # 使用线程池替代进程池
            with ThreadPoolExecutor(
                max_workers=min(os.cpu_count() or 4, len(tasks)),
                initializer=self._init_worker
            ) as executor:
                # 计时开始
                self._timings['pool_init'] = time.perf_counter() - task_start

                # 任务分发
                task_start = time.perf_counter()
                futures = {
                    executor.submit(self._process_wrapper, task, final_params): task
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
            # 添加任务总结日志
            success_rate = len(results) / len(tasks) if tasks else 0
            self._logger.info(
                f"任务完成总结 | 成功率: {success_rate:.1%} | "
                f"成功: {len(results)} | 失败: {len(tasks) - len(results)}"
            )
            self._timings['total'] = time.perf_counter() - task_start
            self._print_stats()

    def _generate_tasks(self, input_dir: Path, output_dir: Path) -> Iterable[Tuple[Path, Path]]:
        """添加任务生成日志"""
        self._scan_skipped = 0
        for entry in os.scandir(input_dir):
            src_path = Path(entry.path)
            if entry.is_file() and src_path.suffix.lower() in self._SUPPORTED_EXT:
                dest_path = output_dir / entry.name
                self._logger.debug(f"添加处理任务: {src_path} → {dest_path}")
                yield (src_path, dest_path)
            else:
                self._scan_skipped += 1
                self._logger.debug(f"跳过非支持文件: {src_path}")

    @staticmethod
    def _init_worker():
        """增强工作线程日志"""
        thread_id = threading.get_ident()
        logger = logging.getLogger()
        logger.info(f"工作线程启动 | TID: {thread_id} | 准备就绪")

    def _process_wrapper(self, task: Tuple[Path, Path], kwargs: ProcessorParams) -> Tuple[bool, Path]:
        """添加详细任务日志"""
        input_path, output_path = task
        thread_name = threading.current_thread().name
        try:
            # 任务开始日志
            self._logger.info(
                f"开始处理文件 | 线程: {thread_name} | "
                f"输入: {input_path} | 输出: {output_path}"
            )
            start_time = time.perf_counter()
            self.process_single(input_path, output_path, kwargs)
            cost = time.perf_counter() - start_time
            self._task_stats['process_single']['count'] += 1
            self._task_stats['process_single']['total'] += cost
            # 成功日志
            self._logger.info(
                f"处理成功 | 线程: {thread_name} | "
                f"耗时: {cost:.2f}s | 输出文件: {output_path}"
            )
            return (True, output_path)
        except Exception as e:
            # 失败日志（包含异常类型）
            error_type = type(e).__name__
            self._logger.error(
                f"处理失败 | 线程: {thread_name} | "
                f"文件: {input_path} | 错误类型: {error_type} | 详情: {str(e)}",
                exc_info=True
            )
            return (False, output_path)

    def process_single(
        self,
        input_path: Path,
        output_path: Path,
        params: T  # 泛型参数
    ) -> None:
        """具体处理逻辑（需子类实现）"""
        self._validate_params(params)
        raise NotImplementedError

    def _validate_params(self, params: T):
        """返回具体参数类型（子类实现）"""
        raise NotImplementedError

    @property
    def log_system(self) -> LogSystem:
        return self._log_system

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def config(self):
        return self._config

    def _parse_config(self, config):
        return {**config}
