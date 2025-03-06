from pathlib import Path
from typing import Type, TypeVar

import yaml

T = TypeVar("T", bound="BaseModel")

class ConfigLoader:
    @classmethod
    def load_config(cls, config_path: Path, model: Type[T]) -> T:
        """安全加载并验证配置"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                raw_config = yaml.safe_load(f)
                return model(**raw_config)
        except FileNotFoundError:
            raise RuntimeError(f"配置文件不存在: {config_path}")
        except yaml.YAMLError as e:
            raise RuntimeError(f"YAML解析失败: {str(e)}")