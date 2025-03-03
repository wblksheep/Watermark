import numpy as np
from PIL import Image

def enhance_watermark_brightness(base_image, watermark_image, boost_ratio=1.2):
    """
    基于背景最大亮度增强水印亮度

    参数：
    base_image: 背景图（PIL.Image, RGB/RGBA）
    watermark_image: 水印图（PIL.Image, RGBA）
    boost_ratio: 亮度提升系数（默认比背景最亮处亮20%）

    返回：
    合成后的PIL.Image (RGBA)
    """
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
        return np.where(rgb <= 0.04045, rgb/12.92, ((rgb+0.055)/1.055)**2.4)

    base_lum = 0.2126 * gamma_correct(base_rgb[...,0]) + \
               0.7152 * gamma_correct(base_rgb[...,1]) + \
               0.0722 * gamma_correct(base_rgb[...,2])
    max_bg_lum = np.max(base_lum)  # 获取背景最亮区域亮度

    # 计算需要达到的目标亮度
    target_lum = min(max_bg_lum * boost_ratio, 1.0)  # 限制不超过最大亮度

    # 计算水印当前亮度
    wm_current_lum = 0.2126 * gamma_correct(wm_rgb[...,0]) + \
                     0.7152 * gamma_correct(wm_rgb[...,1]) + \
                     0.0722 * gamma_correct(wm_rgb[...,2])

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

# 使用示例
base_img = Image.open(r"C:\Users\Design-10\Desktop\ImageTransfer_Admin_v2.0\watermark-images\雾状网格较宽松短距薄透明线\input\input.png")
scale = 2000 / base_img.height
width = int(base_img.width*scale)
base_img = base_img.resize((width, 2000))
watermark_npy = np.load(r"C:\Users\Design-10\Desktop\ImageTransfer_Admin_v2.0\watermark-images\雾状网格较宽松短距薄透明线\watermark_image_450.npy")  # RGBA格式numpy数组
watermark_img = Image.fromarray(watermark_npy)

result_img = enhance_watermark_brightness(base_img, watermark_img, boost_ratio=1.3)
result_img.save(r"C:\Users\Design-10\Desktop\ImageTransfer_Admin_v2.0\watermark-images\雾状网格较宽松短距薄透明线\output.png")