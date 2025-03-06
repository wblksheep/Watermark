from pathlib import Path
from src.config import ModelParams
from src.factory.processor_factory import ProcessorFactory
import logging

logger = logging.getLogger(__name__)

class WatermarkModel:
    def __init__(self):
        self.config = None
        self.processor_factory = None

    def dependency_inject_after_init(self, model_config: ModelParams):
        self.config=model_config
        self.processor_factory = ProcessorFactory(self.config)

    def get_watermark_config(self):
        return self.config

    def get_handler(self, wm_type):
        return getattr(self, self.config.watermark_types[wm_type]['handler'])



    def process_normal_watermark(self, folder,  **kwargs):
        processor = self.processor_factory.create_processor("normal")
        output_dir = self._prepare_output_dir()
        return processor.process_batch(folder, output_dir, **kwargs)

    def process_foggy_watermark(self, folder, text="BH", **kwargs):
        """根据类型处理文件"""
        processor = self.processor_factory.create_processor("foggy")
        output_dir = self._prepare_output_dir()
        return processor.process_batch(folder, output_dir)

    def _prepare_output_dir(self) -> Path:
        """创建输出目录（复用逻辑）"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        return output_dir

    def load_watermark_config(self):
        return self.config

if __name__ == "__main__":
    # 测试代码
    model = WatermarkModel()
    for wm_type in model.config:
        # 检查闭包变量
        handler = model.get_handler(wm_type)
        handler('', **{'allowed_formats': 'jpg', 'default_opacity': -1})
