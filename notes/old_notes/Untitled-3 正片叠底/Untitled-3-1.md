把效果应用在输入图像中
---- v3
如果你希望将水印效果直接应用在输入图像中（即覆盖原始图像），而不是创建一个新的图像文件，可以通过以下方式实现。代码会直接在输入图像上添加水印并应用正片叠底效果，然后覆盖保存原始图像。

以下是更新后的代码：

### 示例代码

```python
from PIL import Image, ImageDraw, ImageFont, ImageChops

def add_watermark_with_multiply(input_image_path, watermark_text, font_path=None, font_size=40, opacity=128):
    """
    对图像加水印并应用正片叠底效果，直接覆盖原始图像。

    :param input_image_path: 输入图像路径
    :param watermark_text: 水印文本
    :param font_path: 字体文件路径（可选，默认使用系统字体）
    :param font_size: 字体大小（默认40）
    :param opacity: 水印透明度（0-255，默认128）
    """
    # 打开原始图像
    base_image = Image.open(input_image_path).convert("RGBA")

    # 创建一个与原始图像大小相同的透明图层
    watermark = Image.new("RGBA", base_image.size, (0, 0, 0, 0))

    # 加载字体
    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except IOError:
        print("字体文件加载失败，使用默认字体。")
        font = ImageFont.load_default()

    # 创建绘图对象
    draw = ImageDraw.Draw(watermark)

    # 计算水印文本的位置（居中）
    text_width, text_height = draw.textsize(watermark_text, font=font)
    x = (base_image.width - text_width) // 2
    y = (base_image.height - text_height) // 2

    # 绘制水印文本
    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, opacity))

    # 应用正片叠底效果
    watermarked_image = ImageChops.multiply(base_image, watermark)

    # 覆盖保存原始图像
    watermarked_image.save(input_image_path, "PNG")
    print(f"水印已添加并覆盖保存到 {input_image_path}")

# 示例用法
if __name__ == "__main__":
    input_image_path = "input_image.jpg"  # 输入图像路径
    watermark_text = "Watermark"  # 水印文本
    font_path = "arial.ttf"  # 字体文件路径（可选）
    font_size = 40  # 字体大小
    opacity = 128  # 水印透明度

    add_watermark_with_multiply(input_image_path, watermark_text, font_path, font_size, opacity)
```

---

### 代码说明

1. **覆盖保存**：

   - 使用 `watermarked_image.save(input_image_path, "PNG")` 将处理后的图像直接覆盖保存到原始图像路径。

2. **其他部分**：
   - 其余部分与之前的代码相同，包括加载图像、创建水印图层、绘制水印文本和应用正片叠底效果。

---

### 运行效果

1. 输入图像会被加载并添加水印。
2. 水印文本会居中显示在图像上，并应用正片叠底效果。
3. 处理后的图像会直接覆盖保存到原始图像路径。

---

### 示例输入和输出

- **输入图像**：`input_image.jpg`
- **水印文本**：`"Watermark"`

运行代码后，输入图像将被直接修改，包含水印并应用正片叠底效果。

---

### 注意事项

- 覆盖保存会直接修改原始图像文件，建议在处理前备份原始图像。
- 如果输入图像不是 PNG 格式，保存时会自动转换为 PNG 格式。如果需要保留原始格式，可以调整保存逻辑。

希望这段代码能满足你的需求！如果有其他问题，请随时告诉我。
