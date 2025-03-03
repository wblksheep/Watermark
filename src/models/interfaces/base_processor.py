import logging
import multiprocessing as mp
from logging.handlers import QueueHandler
from pathlib import Path
from typing import Optional, List
from .interfaces import IWatermarkProcessor, IWatermarkConfig

class BaseWatermarkProcessor(IWatermarkProcessor):
    """水印处理基类"""

    def __init__(self, config: IWatermarkConfig):
        self._config = config
        self._log_queue: Optional[mp.Queue] = None
        self._logger: Optional[logging.Logger] = None

    def process_batch(self, input_dir: Path, output_dir: Path) -> List[Path]:
        """实现批量处理逻辑"""
        output_dir.mkdir(exist_ok=True)

        with mp.Pool(
            processes=mp.cpu_count(),
            initializer=self._init_worker,
            initargs=(self._log_queue,)
        ) as pool:
            tasks = self._generate_tasks(input_dir, output_dir)
            results = pool.starmap(self.process_single, tasks)

        return [Path(t[1]) for t, r in zip(tasks, results) if r]

    def _generate_tasks(self, input_dir: Path, output_dir: Path):
        """生成处理任务元组"""
        return [
            (str(img_path), str(output_dir / img_path.name))
            for img_path in input_dir.glob('*')
            if img_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}
        ]

    def _init_worker(self, log_queue: mp.Queue):
        """初始化工作进程"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        logger.handlers = [QueueHandler(log_queue)]

    @property
    def logger(self) -> logging.Logger:
        if not self._logger:
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger