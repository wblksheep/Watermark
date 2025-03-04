import threading
import time
import logging
import queue
from logging.handlers import QueueHandler, QueueListener
from concurrent.futures import ThreadPoolExecutor

class ThreadLoggingSystem:
    """线程安全日志系统（单例模式）"""
    _instance = None
    _lock = threading.Lock()  # 确保线程安全的单例初始化

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._setup_logging()
        return cls._instance

    @classmethod
    def _setup_logging(cls):
        """配置日志系统"""
        # 创建线程安全的日志队列
        cls.log_queue = queue.Queue(-1)  # 无大小限制

        # 定义日志处理器
        file_handler = logging.FileHandler(
            "threaded.log",
            encoding='utf-8',
            delay=True  # 延迟打开文件直到有日志写入
        )
        console_handler = logging.StreamHandler()

        # 统一日志格式（增加线程ID显示）
        formatter = logging.Formatter(
            "%(asctime)s | TID:%(thread)-5d | %(levelname)-8s | %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 启动监听器（后台线程处理日志）
        cls.listener = QueueListener(
            cls.log_queue,
            file_handler,
            console_handler,
            respect_handler_level=True
        )
        cls.listener.start()

    @classmethod
    def worker_config(cls):
        """工作线程日志配置"""
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        # 添加队列处理器（非阻塞模式）
        logger.addHandler(QueueHandler(cls.log_queue))

    @classmethod
    def shutdown(cls):
        """安全关闭日志系统"""
        cls.listener.stop()
        # 等待队列中的日志处理完成
        while not cls.log_queue.empty():
            time.sleep(0.1)

class ThreadTaskBase:
    """多线程任务基类"""
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.logger = logging.getLogger(self.__class__.__name__)
        # 初始化日志系统
        ThreadLoggingSystem()

    def run_tasks(self, task_list):
        """执行任务入口"""
        self.logger.info(f"启动线程池，最大线程数: {self.max_workers}")
        try:
            with ThreadPoolExecutor(
                max_workers=self.max_workers,
                initializer=self._init_worker
            ) as executor:
                # 提交任务并获取结果
                futures = [executor.submit(self.worker_method, item) for item in task_list]
                return [future.result() for future in futures]
        except Exception as e:
            self.logger.error(f"任务执行失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def _init_worker():
        """工作线程初始化"""
        ThreadLoggingSystem.worker_config()
        logging.info(f"线程 {threading.get_ident()} 就绪")

    def worker_method(self, item):
        """需子类实现的具体任务逻辑"""
        raise NotImplementedError

class SquareCalculator(ThreadTaskBase):
    """平方计算实现类"""
    def worker_method(self, number):
        try:
            start = time.perf_counter()
            # 模拟I/O密集型操作
            time.sleep(0.5)
            result = number ** 2
            cost = time.perf_counter() - start
            logging.info(f"计算结果: {number}² = {result} (耗时{cost:.3f}s)")
            return result
        except Exception as e:
            logging.error(f"处理失败: {number} - {str(e)}")
            raise

if __name__ == '__main__':
    # 配置基础日志
    logging.basicConfig(level=logging.INFO)

    try:
        # 初始化日志系统
        log_system = ThreadLoggingSystem()

        # 创建计算实例
        calculator = SquareCalculator(max_workers=3)

        # 执行任务
        results = calculator.run_tasks([1, 2, 3, 4, 5])
        logging.info(f"最终结果: {results}")

    except Exception as e:
        logging.critical(f"主程序异常: {str(e)}", exc_info=True)
    finally:
        ThreadLoggingSystem.shutdown()
        logging.info("程序正常退出")