import yaml
from pathlib import Path

from src.models.interfaces.interfaces import IWatermarkConfig


class YamlWatermarkConfig(IWatermarkConfig):
    """YAML配置加载器"""

    def __init__(self, config_path: Path):
        with open(config_path) as f:
            self._config = yaml.safe_load(f)['watermark']

    @property
    def output_height(self) -> int:
        return self._config['output_height']

    @property
    def quality(self) -> int:
        return int(self._config['quality'])

    @property
    def opacity(self) -> float:
        return float(self._config['opacity'])