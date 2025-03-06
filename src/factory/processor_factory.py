from src.config_loader.config.yaml_watermark_config import YamlWatermarkConfig
from src.models.interfaces.base_processor import BaseWatermarkProcessor
from src.models.interfaces.impl.foggy_processor import FoggyWatermarkProcessor
from src.models.interfaces.impl.normal_processor import NormalWatermarkProcessor



class ProcessorFactory:
    """支持动态类型配置的处理器工厂"""
    _PROCESSOR_MAP = {
        'normal': NormalWatermarkProcessor,
        'foggy': FoggyWatermarkProcessor
    }

    def __init__(self, config):
        self.config = config

    def create_processor(self, wm_type: str) -> BaseWatermarkProcessor:
        """根据类型创建处理器"""
        if wm_type not in self._PROCESSOR_MAP:
            raise ValueError(f"未注册的处理器类型: {wm_type}")

        # 获取类型化配置
        processor_config = self.config.watermark_types[wm_type]

        return self._PROCESSOR_MAP[wm_type](
            config=processor_config,
            npy_path=processor_config['npy_path']
        )

    # def create_normal_processor(self) -> BaseWatermarkProcessor:
    #     return NormalWatermarkProcessor(
    #         config=self.config,
    #         npy_path=self.config.npy_path  # 从配置中读取路径
    #     )
    # def create_foggy_processor(self) -> BaseWatermarkProcessor:
    #     return FoggyWatermarkProcessor(
    #         config=self.config,
    #         npy_path=self.config.npy_path  # 从配置中读取路径
    #     )