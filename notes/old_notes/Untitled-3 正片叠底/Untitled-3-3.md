举各种不同颜色正片叠底的效果展示。显示一下效果，使用 RGBA 四通道结果。颜色示例由你自己产生。

下面是用 Python 代码实现上述颜色正片叠底效果的示例。我们将使用 `PIL`（Python Imaging Library）库来处理颜色和 RGBA 通道。

### 安装依赖

首先，确保安装了 `PIL` 库（通过 `Pillow` 包）：

```bash
pip install Pillow
```

### Python 代码实现

```python
from PIL import Image, ImageDraw

def multiply_colors(color1, color2):
    """正片叠底混合两个颜色"""
    r1, g1, b1, a1 = color1
    r2, g2, b2, a2 = color2
    r = (r1 * r2) // 255
    g = (g1 * g2) // 255
    b = (b1 * b2) // 255
    a = (a1 * a2) // 255
    return (r, g, b, a)

def create_color_swatch(color, size=(100, 100)):
    """创建一个颜色方块"""
    image = Image.new("RGBA", size, color)
    return image

def main():
    # 定义颜色
    colors = [
        ((255, 0, 0, 255), (0, 255, 0, 255)),  # 示例 1
        ((255, 255, 0, 255), (0, 0, 255, 255)),  # 示例 2
        ((128, 128, 128, 255), (128, 128, 128, 255)),  # 示例 3
        ((255, 128, 64, 255), (64, 128, 255, 255)),  # 示例 4
        ((255, 255, 255, 255), (128, 128, 128, 255)),  # 示例 5
        ((255, 0, 0, 128), (0, 255, 0, 128)),  # 示例 6
        ((255, 128, 64, 192), (64, 128, 255, 192)),  # 示例 7
        ((255, 255, 255, 128), (128, 128, 128, 128)),  # 示例 8
    ]

    # 创建结果图像
    result_image = Image.new("RGBA", (100 * len(colors), 300), (255, 255, 255, 255))
    draw = ImageDraw.Draw(result_image)

    for i, (color1, color2) in enumerate(colors):
        # 计算正片叠底结果
        result_color = multiply_colors(color1, color2)

        # 创建颜色方块
        swatch1 = create_color_swatch(color1)
        swatch2 = create_color_swatch(color2)
        swatch_result = create_color_swatch(result_color)

        # 将方块拼接到结果图像中
        result_image.paste(swatch1, (i * 100, 0))
        result_image.paste(swatch2, (i * 100, 100))
        result_image.paste(swatch_result, (i * 100, 200))

        # 添加标签
        draw.text((i * 100 + 10, 10), "Color1", fill="black")
        draw.text((i * 100 + 10, 110), "Color2", fill="black")
        draw.text((i * 100 + 10, 210), "Result", fill="black")

    # 保存结果
    result_image.save("color_multiply_result.png")
    result_image.show()

if __name__ == "__main__":
    main()
```

### 代码说明

1. **`multiply_colors` 函数**：计算两个颜色的正片叠底结果。
2. **`create_color_swatch` 函数**：创建一个指定颜色的方块图像。
3. **`main` 函数**：
   - 定义了一系列颜色对。
   - 对每对颜色计算正片叠底结果。
   - 将原始颜色和结果颜色拼接成一张大图，并添加标签。
   - 保存并显示结果图像。

### 运行结果

运行代码后，会生成一张图像，显示每对颜色及其正片叠底结果。图像分为三行：

- 第一行：`Color1`（原始颜色 1）。
- 第二行：`Color2`（原始颜色 2）。
- 第三行：`Result`（正片叠底结果）。

### 示例输出

生成的图像会显示以下内容：

1. 红色和绿色的正片叠底结果为黑色。
2. 黄色和蓝色的正片叠底结果为黑色。
3. 中灰色和中灰色的正片叠底结果为深灰色。
4. 橙色和浅蓝色的正片叠底结果为深灰色。
5. 白色和中灰色的正片叠底结果为中灰色。
6. 半透明红色和半透明绿色的正片叠底结果为半透明黑色。
7. 半透明橙色和半透明浅蓝色的正片叠底结果为半透明深灰色。
8. 半透明白色和半透明中灰色的正片叠底结果为半透明中灰色。

希望这段代码能帮助你理解正片叠底的效果！

水印的灰度选择通常取决于背景图像的亮度和对比度，以确保水印既可见又不影响主要内容。一般来说，水印的灰度值在 **20% 到 50%** 之间较为常见，具体选择如下：

1. **浅色背景**：使用较深的水印灰度（如 **30%-50%** 的灰度），以确保水印清晰可见。
2. **深色背景**：使用较浅的水印灰度（如 **20%-30%** 的灰度），以避免水印过于突兀。
3. **中性背景**：选择中等灰度（如 **25%-40%** 的灰度），以平衡可见性和美观性。

此外，水印的透明度（不透明度）通常设置在 **20%-50%** 之间，以进一步降低对主内容的干扰。具体灰度值可以根据实际效果调整，确保水印既能起到标识作用，又不会喧宾夺主。
