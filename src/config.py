import logging
from typing import Dict

import yaml
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ModelParams(BaseModel):
    watermark_types: Dict[str, Dict]

class ViewParams(BaseModel):
    watermark_types: Dict[str, Dict]

class AppConfig(BaseModel):
    """全局应用配置"""
    env: str = Field("dev", pattern="^(dev|test|prod)$")
    log_level: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")
    view_params: ViewParams
    model_params: ModelParams


def setup_logging():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )