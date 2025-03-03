你这个代码并没有根据背景亮度动态调整水印颜色

----- v3

你说得对！之前的代码没有实现根据背景亮度动态调整水印颜色的功能。下面是一个改进的版本，它会根据背景亮度动态调整水印颜色（深色背景用白色水印，浅色背景用黑色水印），并将水印平铺或分散到多个位置。

---

### 改进后的代码

```python
from PIL import Image, ImageDraw, ImageFont
import random

def calculate_brightness(image, x, y, text_width, text_height):
    """计算指定区域的平均亮度"""
    region = image.crop((x, y, x + text_width, y + text_height))
    grayscale = region.convert("L")
    histogram = grayscale.histogram()
    brightness = sum(i * v for i, v in enumerate(histogram)) / (text_width * text_height)
    return brightness

def add_tiled_watermark(image, text, font_path="arial.ttf", font_size=30, spacing=100):
    """平铺水印，并根据背景亮度动态调整颜色"""
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = draw.textsize(text, font=font)

    for x in range(0, image.width, text_width + spacing):
        for y in range(0, image.height, text_height + spacing):
            brightness = calculate_brightness(image, x, y, text_width, text_height)
            watermark_color = "black" if brightness > 127 else "white"
            draw.text((x, y), text, font=font, fill=watermark_color)
    return image

def add_scattered_watermark(image, text, font_path="arial.ttf", font_size=30, positions=None):
    """分散水印，并根据背景亮度动态调整颜色"""
    if positions is None:
        positions = [
            (10, 10),  # 左上
            (image.width - 150, 10),  # 右上
            (10, image.height - 50),  # 左下
            (image.width - 150, image.height - 50),  # 右下
            (image.width // 2 - 75, image.height // 2 - 25),  # 中心
        ]

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = draw.textsize(text, font=font)

    for pos in positions:
        x, y = pos
        brightness = calculate_brightness(image, x, y, text_width, text_height)
        watermark_color = "black" if brightness > 127 else "white"
        draw.text((x, y), text, font=font, fill=watermark_color)
    return image

def add_random_watermark(image, text, font_path="arial.ttf", font_size=30, num_watermarks=10):
    """随机分布水印，并根据背景亮度动态调整颜色"""
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = draw.textsize(text, font=font)

    for _ in range(num_watermarks):
        x = random.randint(0, image.width - text_width)
        y = random.randint(0, image.height - text_height)
        brightness = calculate_brightness(image, x, y, text_width, text_height)
        watermark_color = "black" if brightness > 127 else "white"
        draw.text((x, y), text, font=font, fill=watermark_color)
    return image

# 示例
image = Image.open("example.jpg")

# 平铺水印
tiled_image = add_tiled_watermark(image, "Watermark")
tiled_image.save("tiled_watermark.jpg")
tiled_image.show()

# 分散水印
scattered_image = add_scattered_watermark(image, "Watermark")
scattered_image.save("scattered_watermark.jpg")
scattered_image.show()

# 随机分布水印
random_image = add_random_watermark(image, "Watermark")
random_image.save("random_watermark.jpg")
random_image.show()
```

---

### 代码说明

1. **`calculate_brightness` 函数**：

   - 计算指定区域的平均亮度。
   - 将区域转换为灰度图，然后计算亮度值。

2. **`add_tiled_watermark` 函数**：

   - 将水印平铺在整个图片上。
   - 在每个水印位置计算背景亮度，动态调整水印颜色。

3. **`add_scattered_watermark` 函数**：

   - 将水印分散到图片的多个位置。
   - 在每个水印位置计算背景亮度，动态调整水印颜色。

4. **`add_random_watermark` 函数**：

   - 将水印随机分布在图片上。
   - 在每个水印位置计算背景亮度，动态调整水印颜色。

5. **动态调整水印颜色**：
   - 如果背景亮度大于 127（浅色背景），使用黑色水印。
   - 如果背景亮度小于等于 127（深色背景），使用白色水印。

---

### 效果

- **平铺水印**：水印均匀覆盖整个图片，颜色根据背景动态调整。
- **分散水印**：水印分布在关键位置，颜色根据背景动态调整。
- **随机分布水印**：水印随机分布在图片上，颜色根据背景动态调整。

---

### 示例图片

假设有一张图片 `example.jpg`，运行代码后会生成以下图片：

1. `tiled_watermark.jpg`：平铺水印。
2. `scattered_watermark.jpg`：分散水印。
3. `random_watermark.jpg`：随机分布水印。

---

### 总结

通过动态调整水印颜色，可以确保水印在不同背景上都清晰可见。结合平铺、分散或随机分布的方法，可以进一步提高水印的覆盖范围和美观性。
