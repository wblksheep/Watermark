import numpy as np
from PIL import Image

def adaptive_watermark(base_image, watermark_image, alpha=0.7, contrast_ratio=3):
    """
    基于基础图像亮度动态调整水印

    参数：
    base_image：PIL.Image格式的基础图像
    watermark_image：PIL.Image格式的水印图像
    alpha：水印基础透明度（0-1）
    contrast_ratio：期望达到的最小对比度

    返回：
    合成后的PIL.Image图像
    """
    # 转换为RGB模式并确保尺寸一致
    # base = base_image.convert("RGB")
    # watermark = watermark_image.convert("RGB").resize(base.size)

    # 获取图片和水印的尺寸
    base_width, base_height = base_image.size
    watermark_width, watermark_height = watermark_image.size
    
    if watermark_width > base_width or watermark_height > base_height:
        watermark_image = watermark_image.crop((0,0, base_width, base_height))
    
    base = base_image.convert("RGBA")
    watermark = watermark_image.convert("RGBA")
    # watermark_image.show()
    # 转换为numpy数组
    base_arr = np.array(base).astype(np.float32) / 255.0
    watermark_arr = np.array(watermark).astype(np.float32) / 255.0

    # 计算基础图像亮度图（WCAG标准）
    def get_luminance(rgb):
        r_lin = np.where(rgb[:,:,0] <= 0.04045, rgb[:,:,0]/12.92, ((rgb[:,:,0]+0.055)/1.055)**2.4)
        g_lin = np.where(rgb[:,:,1] <= 0.04045, rgb[:,:,1]/12.92, ((rgb[:,:,1]+0.055)/1.055)**2.4)
        b_lin = np.where(rgb[:,:,2] <= 0.04045, rgb[:,:,2]/12.92, ((rgb[:,:,2]+0.055)/1.055)**2.4)
        return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

    base_lum = get_luminance(base_arr)  # 基础图像亮度矩阵
    watermark_lum = get_luminance(watermark_arr)  # 水印原始亮度

    # 动态调整参数计算
    target_lum = np.clip(base_lum, 0.2, 0.8)  # 亮度补偿策略
    scale_factor = np.where(
        base_lum > watermark_lum,
        (base_lum + 0.05) / (watermark_lum + 0.05),
        (watermark_lum + 0.05) / (base_lum + 0.05)
    )

    # 保持色相调整亮度
    adjusted_watermark = np.zeros_like(watermark_arr)
    for c in range(3):
        channel = watermark_arr[:,:,c]
        adjusted = channel * scale_factor
        adjusted_watermark[:,:,c] = np.clip(adjusted, 0, 1)
    watermark = Image.fromarray((adjusted_watermark*255).astype(np.uint8))
    watermark.show()
    # 透明度混合
    blended = alpha * adjusted_watermark + (1 - alpha) * base_arr
    return Image.fromarray((blended * 255).astype(np.uint8))

# 使用示例
base = Image.open(r"C:\Users\Design-10\Desktop\ImageTransfer_Admin_v2.0\watermark-images\雾状网格较宽松短距薄透明线\input\input.png")
watermark_npy = np.load(r"C:\Users\Design-10\Desktop\ImageTransfer_Admin_v2.0\watermark-images\雾状网格较宽松短距薄透明线\watermark_image_450.npy")
watermark = Image.fromarray(watermark_npy)

result = adaptive_watermark(base, watermark, alpha=0.7)
result.save(r"C:\Users\Design-10\Desktop\ImageTransfer_Admin_v2.0\watermark-images\雾状网格较宽松短距薄透明线\output.jpg")