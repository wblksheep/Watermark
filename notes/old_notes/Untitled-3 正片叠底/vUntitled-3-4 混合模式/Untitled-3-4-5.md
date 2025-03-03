正片叠底如何做到在深色背景下使水印变亮的？

------- v3

正片叠底（Multiply）是一种常见的混合模式，通常会使图像变暗，因为它是通过将两个图像的像素值相乘来实现的。然而，在深色背景下，正片叠底会使水印变得更暗，而不是变亮。如果希望在深色背景下使水印变亮，可以使用**反相正片叠底**或**屏幕混合模式**。

以下是使用 PIL 实现水印在深色背景下变亮的方法：

---

### 方法 1：使用**反相正片叠底**

反相正片叠底的核心思想是将水印反相后再进行正片叠底混合，这样可以在深色背景下使水印变亮。

```python
from PIL import Image, ImageChops

def invert_multiply_blend(base, overlay):
    """
    反相正片叠底混合
    """
    # 反相水印
    inverted_overlay = ImageChops.invert(overlay)
    # 正片叠底混合
    blended = ImageChops.multiply(base, inverted_overlay)
    return blended

# 读取背景图像和水印
background = Image.open("background.jpg").convert("RGB")
watermark = Image.open("watermark.png").convert("RGB")

# 调整水印大小（如果需要）
watermark = watermark.resize(background.size)

# 应用反相正片叠底混合
result = invert_multiply_blend(background, watermark)

# 保存结果
result.save("result_invert_multiply.jpg")

# 显示结果
result.show()
```

---

### 方法 2：使用**屏幕混合模式**

屏幕混合模式可以使水印在深色背景下变亮，因为它是通过将两个图像的像素值反相后相乘再反相来实现的。

```python
from PIL import Image, ImageChops

def screen_blend(base, overlay):
    """
    屏幕混合模式
    """
    # 反相背景和水印
    inverted_base = ImageChops.invert(base)
    inverted_overlay = ImageChops.invert(overlay)
    # 正片叠底混合
    multiplied = ImageChops.multiply(inverted_base, inverted_overlay)
    # 反相结果
    result = ImageChops.invert(multiplied)
    return result

# 读取背景图像和水印
background = Image.open("background.jpg").convert("RGB")
watermark = Image.open("watermark.png").convert("RGB")

# 调整水印大小（如果需要）
watermark = watermark.resize(background.size)

# 应用屏幕混合模式
result = screen_blend(background, watermark)

# 保存结果
result.save("result_screen_blend.jpg")

# 显示结果
result.show()
```

---

### 方法 3：使用**线性减淡混合模式**

线性减淡混合模式可以使水印在深色背景下变亮，因为它会将水印的像素值与背景的像素值相加。

```python
from PIL import Image, ImageChops

def linear_dodge_blend(base, overlay):
    """
    线性减淡混合模式
    """
    # 将水印与背景相加
    blended = ImageChops.add(base, overlay)
    return blended

# 读取背景图像和水印
background = Image.open("background.jpg").convert("RGB")
watermark = Image.open("watermark.png").convert("RGB")

# 调整水印大小（如果需要）
watermark = watermark.resize(background.size)

# 应用线性减淡混合模式
result = linear_dodge_blend(background, watermark)

# 保存结果
result.save("result_linear_dodge.jpg")

# 显示结果
result.show()
```

---

### 方法选择：

- **反相正片叠底**：适合需要水印在深色背景下变亮，同时保留背景细节的场景。
- **屏幕混合模式**：适合需要水印在深色背景下变亮，且水印本身较暗的场景。
- **线性减淡混合模式**：适合需要水印在深色背景下变亮，且水印本身较亮的场景。

---

### 注意事项：

1. 水印图像需要是透明背景的 PNG 格式，或者已经处理为灰度图像。
2. 如果水印颜色较深，可以预先调整水印的亮度或对比度。
3. 混合模式的效果取决于背景和水印的像素值，可以根据需要调整水印的透明度或颜色。

运行代码后，你会得到一张在深色背景下水印变亮的图像。
