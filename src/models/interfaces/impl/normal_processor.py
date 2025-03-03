from pathlib import Path

from PIL import Image
import numpy as np
from ..base_processor import BaseWatermarkProcessor
from ..interfaces import IWatermarkConfig


class NormalWatermarkProcessor(BaseWatermarkProcessor):
    """常规水印处理器"""

    def __init__(self, config: IWatermarkConfig, npy_path: str):
        super().__init__(config)
        self._watermark_data = np.load(npy_path)

    def process_single(self, input_path: Path, output_path: Path) -> bool:
        try:
            with Image.open(input_path) as img:
                processed = self._apply_watermark(img)
                processed.save(output_path, quality=self._config.quality)
                return True
        except Exception as e:
            self.logger.error(f"处理失败: {input_path} - {str(e)}")
            return False

    def _apply_watermark(self, base_image: Image.Image) -> Image.Image:
        """应用水印核心算法"""
        scaled_img = base_image.resize(
            (int(base_image.width * (self._config.output_height / base_image.height)),
             self._config.output_height)
        )

        watermark = Image.fromarray(self._watermark_data).convert('RGBA')
        watermark.putalpha(int(255 * self._config.opacity))

        scaled_img.paste(watermark, (0, 0), watermark)
        return scaled_img.convert('RGB')