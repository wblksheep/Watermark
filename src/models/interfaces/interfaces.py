from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List
import logging

class IWatermarkProcessor(ABC):
    """水印处理核心接口"""

    @abstractmethod
    def process_batch(self, input_dir: Path, output_dir: Path) -> List[Path]:
        """
        批量处理图片
        :param input_dir: 输入目录
        :param output_dir: 输出目录
        :return: 处理成功的文件列表
        """

    @abstractmethod
    def process_single(self, input_path: Path, output_path: Path) -> bool:
        """
        处理单张图片
        :param input_path: 输入文件路径
        :param output_path: 输出文件路径
        :return: 是否处理成功
        """

    @property
    @abstractmethod
    def logger(self) -> logging.Logger:
        """获取绑定的日志记录器"""

class IWatermarkConfig(ABC):
    """水印配置接口"""

    @property
    @abstractmethod
    def output_height(self) -> int:
        """输出图片高度"""

    @property
    @abstractmethod
    def quality(self) -> int:
        """输出质量参数"""

    @property
    @abstractmethod
    def opacity(self) -> float:
        """水印透明度"""