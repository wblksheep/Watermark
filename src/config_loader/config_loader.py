from pathlib import Path

from .config.yaml_watermark_config import YamlWatermarkConfig, WatermarkConfig


class ConfigLoader:
    @classmethod
    def load_yamlwatermark_config(cls)->YamlWatermarkConfig:
        config_path = Path(f"config_loader/config/watermark.yaml")
        return YamlWatermarkConfig(config_path)

    @classmethod
    def load_watermark_config(cls)->WatermarkConfig:
        config_path = Path(f"config.yaml")
        return WatermarkConfig(config_path)
