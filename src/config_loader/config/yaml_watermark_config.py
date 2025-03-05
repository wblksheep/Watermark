from abc import abstractmethod, ABC
from typing import Dict, Any

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

    """配置抽象接口"""
    def get_processor_config(self, wm_type: str) -> Dict[str, Any]:
        raise NotImplementedError
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
            self._raw_config = self._config
            self._validate_config()
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

    def _validate_config(self):
        """配置完整性校验"""
        required_fields = {'npy_path', 'output_height', 'quality'}
        for wm_type, config in self._raw_config['watermark'].items():
            missing = required_fields - config.keys()
            if missing:
                raise ValueError(
                    f"水印类型 {wm_type} 缺少必要配置项: {missing}"
                )
    def get_processor_config(self, wm_type: str) -> Dict[str, Any]:
        """获取类型化配置"""
        type_config = self._raw_config['watermark'].get(wm_type)
        if not type_config:
            raise ValueError(f"不支持的水印类型: {wm_type}")

        return {
            "npy_path": Path(f"{type_config['npy_path']}.npy"),
            "output_height": type_config['output_height'],
            "quality": type_config['quality'],
            "type_params": type_config.get('params', {})
        }