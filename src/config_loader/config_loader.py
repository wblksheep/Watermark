from pathlib import Path

from config.yaml_watermark_config import YamlWatermarkConfig


class ConfigLoader:
    @classmethod
    def load_watermark_config(cls)->YamlWatermarkConfig:
        config_path = Path(f"config/watermark.yaml")
        return YamlWatermarkConfig(config_path)
