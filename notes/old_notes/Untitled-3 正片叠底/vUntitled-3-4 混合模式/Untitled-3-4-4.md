使用 PIL
----- v3

使用 Python 的 PIL（Pillow 库）实现图像柔光处理也非常简单。以下是使用 PIL 实现柔光处理的代码示例：

```python
from PIL import Image, ImageChops, ImageOps
import numpy as np

def soft_light_blend(img1, img2):
    """
    柔光混合公式
    """
    img1 = np.array(img1, dtype=np.float32) / 255.0
    img2 = np.array(img2, dtype=np.float32) / 255.0

    # 柔光混合公式
    result = np.where(img2 <= 0.5,
                      img1 * img2 * 2,
                      1 - (1 - img1) * (1 - img2) * 2)

    # 将结果限制在0-1范围内并转换为8位图像
    result = np.clip(result, 0, 1) * 255
    return Image.fromarray(result.astype(np.uint8))

def apply_soft_light(image, intensity=0.5):
    """
    应用柔光处理
    """
    # 将图像转换为浮点数并归一化
    image = image.convert("RGB")
    width, height = image.size

    # 创建一个柔光层（纯色图像）
    soft_light_layer = Image.new("RGB", (width, height), (int(255 * intensity), int(255 * intensity), int(255 * intensity)))

    # 应用柔光混合
    blended_image = soft_light_blend(image, soft_light_layer)
    return blended_image

# 读取图像
image = Image.open("input_image.jpg")

# 应用柔光处理
soft_light_image = apply_soft_light(image, intensity=0.5)

# 保存结果
soft_light_image.save("soft_light_image.jpg")

# 显示结果
soft_light_image.show()
```

### 代码说明：

1. **soft_light_blend 函数**：

   - 将输入图像转换为 NumPy 数组并归一化到 0-1 范围。
   - 根据柔光公式进行混合：
     - 如果 `img2` 的像素值小于等于 0.5，使用 `img1 * img2 * 2`。
     - 否则，使用 `1 - (1 - img1) * (1 - img2) * 2`。
   - 将结果限制在 0-1 范围内，并转换为 8 位图像。

2. **apply_soft_light 函数**：

   - 将输入图像转换为 RGB 模式。
   - 创建一个纯色图像作为柔光层，颜色由 `intensity` 参数控制。
   - 调用 `soft_light_blend` 函数进行混合。

3. **图像读取与保存**：
   - 使用 PIL 读取图像，并保存处理后的图像。

### 参数调整：

- `intensity`：控制柔光的强度，取值范围为 0 到 1。值越大，柔光效果越明显。

### 依赖库：

- `Pillow`：用于图像处理。
- `NumPy`：用于数值计算和数组操作。

### 注意事项：

- 如果图像是 RGBA 模式（带有透明度通道），需要先转换为 RGB 模式。
- 柔光层的颜色可以根据需要调整，这里使用灰度颜色（`intensity` 控制亮度）。

运行代码后，你会得到一张经过柔光处理的图像，并保存为 `soft_light_image.jpg`。
