```python
from PIL import Image, ImageChops
import numpy as np
import os

def load_npy(npy_path):
    if not os.path.exists(npy_path):
        raise FileNotFoundError(f"npy文件 {npy_path} 不存在")
    return np.load(npy_path)
def overlay_blend(top, bottom):
    # 将图像转换为灰度以计算亮度
    def calculate_overlay(c_top, c_bottom):
        if c_bottom <= 128:
            return 2 * c_top * c_bottom / 255
        else:
            return 255 - 2 * (255 - c_top) * (255 - c_bottom) / 255

    # 对每个像素应用叠加公式
    result = Image.new("RGB", top.size)
    for x in range(top.width):
        for y in range(top.height):
            r_top, g_top, b_top, a_top = top.getpixel((x, y))
            r_bottom, g_bottom, b_bottom, a_bottom = bottom.getpixel((x, y))
            r_result = calculate_overlay(r_top, r_bottom)
            g_result = calculate_overlay(g_top, g_bottom)
            b_result = calculate_overlay(b_top, b_bottom)
            result.putpixel((x, y), (int(r_result), int(g_result), int(b_result)))
    return result


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

background = overlay_blend(background, result)

background.show()
```
