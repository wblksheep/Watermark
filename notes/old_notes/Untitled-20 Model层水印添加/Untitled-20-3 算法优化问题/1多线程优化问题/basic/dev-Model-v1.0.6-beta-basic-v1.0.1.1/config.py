import logging

import yaml
from pathlib import Path
logger = logging.getLogger(__name__)

#
class ConfigLoader:
    @staticmethod
    def load_watermark_config():
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            try:
                config = yaml.safe_load(f)
            except Exception as e:
                logger.exception(e)
                return []
        return config.get("watermark_types", [])

def setup_logging():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )