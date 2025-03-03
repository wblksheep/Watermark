import numpy as np
from PIL import Image

def adapt_rgba_watermark(base_image, watermark_image, min_contrast=4.5):
    """
    RGBA水印自适应亮度调整算法

    参数：
    base_image: PIL.Image (RGB/RGBA)
    watermark_image: PIL.Image (RGBA)
    min_contrast: 最小对比度要求

    返回：
    合成后的PIL.Image (RGBA)
    """
    # # 统一转换为RGBA格式
    # base = base_image.convert("RGBA")
    # watermark = watermark_image.convert("RGBA").resize(base.size)

    # 获取图片和水印的尺寸
    base_width, base_height = base_image.size
    watermark_width, watermark_height = watermark_image.size
    
    if watermark_width > base_width or watermark_height > base_height:
        watermark_image = watermark_image.crop((0,0, base_width, base_height))
    base = base_image.convert("RGBA")
    watermark = watermark_image.convert("RGBA")
    # 获取numpy数组
    base_arr = np.array(base).astype(np.float32) / 255.0
    wm_arr = np.array(watermark).astype(np.float32) / 255.0


    # 分离alpha通道
    base_rgb, base_a = base_arr[..., :3], base_arr[..., 3]
    wm_rgb, wm_alpha = wm_arr[..., :3], wm_arr[..., 3]

    # 计算基础图像亮度（伽马校正后）
    def gamma_correct(rgb):
        return np.where(rgb <= 0.04045, rgb/12.92, ((rgb+0.055)/1.055)**2.4)

    base_lum = 0.2126 * gamma_correct(base_rgb[...,0]) + \
               0.7152 * gamma_correct(base_rgb[...,1]) + \
               0.0722 * gamma_correct(base_rgb[...,2])

    # 计算水印原始亮度
    wm_lum = 0.2126 * gamma_correct(wm_rgb[...,0]) + \
             0.7152 * gamma_correct(wm_rgb[...,1]) + \
             0.0722 * gamma_correct(wm_rgb[...,2])
    
    # 动态亮度调整
    target_lum = np.where(
        base_lum > 0.5,
        np.clip(base_lum + 0.4, 0.1, 0.9),  # 亮背景提高水印亮度
        np.clip(base_lum , 0.1, 0.9)   # 暗背景水印亮度不变
    )
    

    # 保持色相的亮度调整
    scale = (target_lum + 0.05) / (wm_lum + 0.05)
    scale = np.clip(scale, 0.3, 3.0)  # 防止过度调整

    # 应用亮度缩放
    adjusted_rgb = np.zeros_like(wm_rgb)
    for c in range(3):
        adjusted_rgb[..., c] = np.clip(wm_rgb[..., c] * scale, 0, 1)

    # 透明度增强策略
    enhanced_alpha = np.where(
        np.abs(base_lum - target_lum) < 0.3,
        wm_alpha,  # 低对比度区域增强透明度
        wm_alpha
    )
    enhanced_alpha = np.clip(enhanced_alpha, 0, 1)

    # 合成图像
    composite_rgb = adjusted_rgb * enhanced_alpha[..., np.newaxis] + \
                    base_rgb * (1 - enhanced_alpha[..., np.newaxis])
    composite_a = np.maximum(base_a, enhanced_alpha)

    # 重组RGBA
    result = np.concatenate([
        composite_rgb,
        composite_a[..., np.newaxis]
    ], axis=-1)

    return Image.fromarray((result * 255).astype(np.uint8))

# 使用示例
base_img = Image.open(r"C:\Users\Design-10\Desktop\ImageTransfer_Admin_v2.0\watermark-images\雾状网格较宽松短距薄透明线\input\input1.jpg")

scale = 2000 / base_img.height 
width = int(base_img.width * scale)
base_img = base_img.resize((width, 2000))
watermark_npy = np.load(r"C:\Users\Design-10\Desktop\ImageTransfer_Admin_v2.0\watermark-images\雾状网格较宽松短距薄透明线\watermark_image_450.npy")  # 假设为RGBA格式的numpy数组
watermark_img = Image.fromarray(watermark_npy)

result_img = adapt_rgba_watermark(base_img, watermark_img)
result_img.save(r"C:\Users\Design-10\Desktop\ImageTransfer_Admin_v2.0\watermark-images\雾状网格较宽松短距薄透明线\output.png")