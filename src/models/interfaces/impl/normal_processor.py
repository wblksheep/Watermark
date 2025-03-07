import io
import os
from pathlib import Path
from typing import Dict

from PIL import Image
import numpy as np
from ..base_processor import BaseWatermarkProcessor, ProcessorParams
from ..interfaces import IWatermarkConfig

# 参数对象定义
class NormalParams:
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

class NormalWatermarkProcessor(BaseWatermarkProcessor[NormalParams]):
    """常规水印处理器"""

    def __init__(self, config: IWatermarkConfig, npy_path: str):
        super().__init__(config)
        self._watermark_data = np.load(npy_path)

    def load_image(self, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件 {image_path} 不存在")
        return Image.open(image_path)

    # 读取npy文件
    def load_npy(self, npy_path):
        if not os.path.exists(npy_path):
            raise FileNotFoundError(f"npy文件 {npy_path} 不存在")
        return np.load(npy_path)

    def _validate_params(self, params: ProcessorParams) -> NormalParams:
        """转换并校验雾化专用参数"""
        return NormalParams(**params.dict())

    def process_single(
        self,
        input_path: Path,
        output_path: Path,
        params: NormalParams  # 明确类型
    )-> bool:
        # print(f"使用混合模式 {params.kwargs} 处理文件")
        # return True
        try:
            # 加载并预处理图片
            base_image = self.load_image(input_path)
            scale = params.output_height / base_image.height
            width = int(base_image.width * scale)
            base_image = base_image.resize((width, params.output_height))
            if base_image.mode == "RGB":
                buffer = io.BytesIO()
                base_image.save(buffer, format="JPEG", quality=params.quality)
                buffer.seek(0)
                base_image = Image.open(buffer)
            else:
                # PNG 压缩（无损但有压缩级别）
                buffer = io.BytesIO()
                base_image.save(buffer, format="PNG", compress_level=int((100 - params.quality) / 10))  # 最高压缩级别
                buffer.seek(0)
                base_image = Image.open(buffer)
            # # 加载水印数据
            # npy_path = f"{self._watermark_data}.npy"
            # npy_data = load_npy(npy_path) * (opacity/100.0)
            npy_data = self._watermark_data
            np.resize(npy_data, (params.output_height, params.output_height))
            if params.enhancement:
                watermarked = self.enhance_watermark_brightness(base_image, npy_data, final_opacity=params.opacity)
            else:
                # 应用水印
                watermarked = self.overlay_and_crop(base_image, npy_data, final_opacity=float(params.opacity / 100.0))

            if os.path.splitext(output_path)[1] in [".jpeg", ".jpg"]:
                watermarked = watermarked.convert("RGB")
            # 保存结果
            watermarked.save(output_path, quality=100)
            return True
        except Exception as e:
            self.logger.exception(f"处理失败: {input_path} - {str(e)}")
            return False

    # def _validate_params(self, params: T):
    #     # 运行时校验协议实现
    #     if not isinstance(params, ProcessParams):  # 依赖 @runtime_checkable
    #         missing = []
    #         if not hasattr(params, 'opacity'):
    #             missing.append('opacity')
    #         if not hasattr(params, 'blend_mode'):
    #             missing.append('blend_mode')
    #         raise TypeError(f"参数缺少必要属性: {missing}")

    def overlay_and_crop(self, base_image, npy_data, final_opacity=0.75):
        """叠加水印并裁剪"""
        # print(f"npy_data.shape = {npy_data.shape}")
        watermark_image = Image.fromarray(npy_data)
        # 获取图片和水印的尺寸
        base_width, base_height = base_image.size
        watermark_width, watermark_height = watermark_image.size

        # 裁剪水印超出图片的部分
        if watermark_width > base_width or watermark_height > base_height:
            watermark_image = watermark_image.crop((0, 0, base_width, base_height))
        # 设置水印透明度
        # 假设 watermark 是一个 PIL 图像对象
        watermark_image = watermark_image.convert("RGBA")  # 确保图像是 RGBA 模式（带有 alpha 通道）
        # 分离图像的通道
        r, g, b, a = watermark_image.split()

        # 仅对 alpha 通道进行调整
        # aaa = np.asarray(a).astype(np.uint8)
        # a = Image.fromarray(np.trunc(np.where(aaa <= 1, 1, 255*final_opacity)).astype(np.uint8))
        a = a.point(lambda p: int(p * final_opacity))  # 将 alpha 通道的透明度设置为 final_opacity%

        # 重新合并通道
        watermark_image = Image.merge("RGBA", (r, g, b, a))

        # 将水印覆盖到图片的左上角
        base_image.paste(watermark_image, (0, 0), watermark_image)  # 使用alpha通道（如果存在）
        return base_image

    def enhance_watermark_brightness(self, base_image, npy_data, boost_ratio=1.2, final_opacity=0.5):
        """
        基于背景最大亮度增强水印亮度

        参数：
        base_image: 背景图（PIL.Image, RGB/RGBA）
        watermark_image: 水印图（PIL.Image, RGBA）
        boost_ratio: 亮度提升系数（默认比背景最亮处亮20%）

        返回：
        合成后的PIL.Image (RGBA)
        """
        watermark_image = Image.fromarray(npy_data)
        base_width, base_height = base_image.size
        watermark_width, watermark_height = watermark_image.size

        if watermark_width > base_width or watermark_height > base_height:
            watermark_image = watermark_image.crop((0, 0, base_width, base_height))

        # 统一转换为RGBA格式
        base = base_image.convert("RGBA")
        watermark = watermark_image.convert("RGBA")

        # 获取numpy数组并归一化
        base_arr = np.array(base).astype(np.float32) / 255.0
        wm_arr = np.array(watermark).astype(np.float32) / 255.0

        # 分离通道
        base_rgb = base_arr[..., :3]
        wm_rgb = wm_arr[..., :3]
        wm_alpha = wm_arr[..., 3]

        # 计算背景最大亮度（伽马校正后）
        def gamma_correct(rgb):
            return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)

        base_lum = 0.2126 * gamma_correct(base_rgb[..., 0]) + \
                   0.7152 * gamma_correct(base_rgb[..., 1]) + \
                   0.0722 * gamma_correct(base_rgb[..., 2])
        max_bg_lum = np.max(base_lum)  # 获取背景最亮区域亮度

        # 计算需要达到的目标亮度
        target_lum = min(max_bg_lum * boost_ratio, 1.0)  # 限制不超过最大亮度

        # 计算水印当前亮度
        wm_current_lum = 0.2126 * gamma_correct(wm_rgb[..., 0]) + \
                         0.7152 * gamma_correct(wm_rgb[..., 1]) + \
                         0.0722 * gamma_correct(wm_rgb[..., 2])

        # 亮度缩放因子（仅增强不足的区域）
        scale = np.where(
            wm_current_lum < target_lum,
            (target_lum + 0.05) / (wm_current_lum + 0.05),
            1.0  # 已经足够亮的区域不调整
        )
        scale = np.clip(scale, 1.0, 5.0)  # 限制最大缩放倍率

        # 保持色相调整亮度
        adjusted_rgb = np.zeros_like(wm_rgb)
        for c in range(3):
            adjusted_rgb[..., c] = np.clip(wm_rgb[..., c] * scale, 0, 1)

        # 合成图像（考虑透明度）
        composite_rgb = adjusted_rgb * wm_alpha[..., np.newaxis] + \
                        base_rgb * (1 - wm_alpha[..., np.newaxis])
        composite_a = np.maximum(base_arr[..., 3], wm_alpha)

        # 重组RGBA并输出
        result = np.concatenate([
            composite_rgb,
            composite_a[..., np.newaxis]
        ], axis=-1)

        return Image.fromarray((result * 255).astype(np.uint8))