import io
import os
from pathlib import Path
from typing import Dict

from PIL import Image
import numpy as np
from ..base_processor import BaseWatermarkProcessor, ProcessorParams
from ..interfaces import IWatermarkConfig

# 参数对象定义
class FoggyParams:
    """雾化水印参数"""
    opacity: int = 75
    output_height: int = 1000
    quality: int = 30
    enhancement: bool = True
    kwargs: Dict
    """普通水印参数（隐式实现协议）"""
    def __init__(self, opacity: int, output_height: int, quality: int,enhancement: bool, **kwargs):
        self.opacity = opacity
        self.output_height = output_height
        self.quality = quality
        self.enhancement = enhancement
        self.kwargs = kwargs

class FoggyWatermarkProcessor(BaseWatermarkProcessor):
    """常规水印处理器"""

    def __init__(self, config: IWatermarkConfig, npy_path: str):
        super().__init__(config)
        filepath = self.get_resource_path(npy_path)
        self._watermark_data = np.load(filepath)

    def load_image(self, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件 {image_path} 不存在")
        return Image.open(image_path)

    # 读取npy文件
    def load_npy(self, npy_path):
        if not os.path.exists(npy_path):
            raise FileNotFoundError(f"npy文件 {npy_path} 不存在")
        return np.load(npy_path)

    def _validate_params(self, params: ProcessorParams) -> FoggyParams:
        """转换并校验雾化专用参数"""
        return FoggyParams(**params.dict())

    def process_single(self, input_path: Path, output_path: Path, params: FoggyParams) -> bool:
        try:
            # 加载并预处理图片
            base_image = self.load_image(input_path)
            scale = self.config['output_height'] / base_image.height
            width = int(base_image.width * scale)
            base_image = base_image.resize((width, self.config['output_height']))
            if base_image.mode == "RGB":
                buffer = io.BytesIO()
                base_image.save(buffer, format="JPEG", quality=self.config['quality'])
                buffer.seek(0)
                base_image = Image.open(buffer)
            else:
                # PNG 压缩（无损但有压缩级别）
                buffer = io.BytesIO()
                base_image.save(buffer, format="PNG", compress_level=int((100 - self.config['quality']) / 10))  # 最高压缩级别
                buffer.seek(0)
                base_image = Image.open(buffer)
            # # 加载水印数据
            # npy_path = f"{self._watermark_data}.npy"
            # npy_data = load_npy(npy_path) * (opacity/100.0)
            npy_data = self._watermark_data
            np.resize(npy_data, (self.config['output_height'], self.config['output_height']))
            # 应用水印
            watermarked = self.overlay_and_crop(base_image, npy_data)

            if os.path.splitext(output_path)[1] in [".jpeg", ".jpg"]:
                watermarked = watermarked.convert("RGB")
            # 保存结果
            watermarked.save(output_path, quality=100)
            return True
        except Exception as e:
            self.logger.exception(f"处理失败: {input_path} - {str(e)}")
            return False

    def overlay_and_crop(self, base_image, npy_data):
        """叠加水印并裁剪"""
        # print(f"npy_data.shape = {npy_data.shape}")
        watermark_image = Image.fromarray(npy_data)
        # 获取图片和水印的尺寸
        base_width, base_height = base_image.size
        watermark_width, watermark_height = watermark_image.size

        # 裁剪水印超出图片的部分
        if watermark_width > base_width or watermark_height > base_height:
            watermark_image = watermark_image.crop((0, 0, base_width, base_height))

        # 将水印覆盖到图片的左上角
        base_image.paste(watermark_image, (0, 0), watermark_image)  # 使用alpha通道（如果存在）
        return base_image