from abc import abstractmethod, ABC

import yaml
from pathlib import Path

from src.models.interfaces.interfaces import IWatermarkConfig

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

    # @property
    # @abstractmethod
    # def config(self):
    #     """配置"""
    # @property
    # @abstractmethod
    # def npy_path(self) -> str:
    #     """水印透明度"""

class YamlWatermarkConfig(IWatermarkConfig):
    """YAML配置加载器"""

    def __init__(self, config_path: Path):
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    @property
    def output_height(self) -> int:
        return self._config['watermark']['output_height']

    @property
    def quality(self) -> int:
        return int(self._config['watermark']['quality'])

    @property
    def opacity(self) -> float:
        return float(self._config['watermark']['opacity'])

class WatermarkConfig(IWatermarkConfig):
    """YAML配置加载器"""

    def __init__(self, config_path: Path):
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    @property
    def output_height(self) -> int:
        return self._config['watermark']['output_height']

    @property
    def quality(self) -> int:
        return int(self._config['watermark']['quality'])

    @property
    def opacity(self) -> float:
        return float(self._config['watermark']['opacity'])

    @property
    def config(self):
        return self._config['watermark_types']

    @property
    def npy_path(self):
        return Path(f"{self._config['watermark']['npy_path']}.npy")