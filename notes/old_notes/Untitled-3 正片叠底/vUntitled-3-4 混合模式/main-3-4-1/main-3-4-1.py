from PIL import Image, ImageChops
import numpy as np
import os

def load_npy(npy_path):
    if not os.path.exists(npy_path):
        raise FileNotFoundError(f"npy文件 {npy_path} 不存在")
    return np.load(npy_path)

# 加载背景图像和水印图像
background = Image.open("input.jpg").convert("RGBA")
npy_path = "watermark_image_600.npy"
# watermark = Image.open("watermark_image_with_emboss.png").convert("RGBA").resize(background.size)
npy_data = load_npy(npy_path)
watermark = Image.fromarray(npy_data).resize(background.size)
watermark.show()

# 设置水印透明度
watermark = watermark.point(lambda p: int(p * 1))  # 50% 透明度

# 对背景和水印进行正片叠底处理
result = ImageChops.multiply(background.convert("RGB"), watermark.convert("RGB"))
result = result.convert("RGBA")

print(watermark.getchannel("A"))

# 将水印的透明度应用到结果
result.putalpha(watermark.getchannel("A"))

# 保存或显示结果
result.show()

background.paste(result,(0,0), result)

background.show()