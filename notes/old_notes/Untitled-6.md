读取一个 mask，将其中为 1 的数据设置为 color: (200, 200, 200, 255)，将其中为 0 的数据设为透明
---- v3

要将一个掩码（`mask`）中值为 `1` 的数据设置为颜色 `(200, 200, 200, 255)`，值为 `0` 的数据设置为透明，可以按照以下步骤实现：

### 实现代码：

```python
import numpy as np
from PIL import Image

# 读取掩码文件（假设是 .npy 文件）
mask = np.load("watermark_mask.npy")  # 掩码的形状为 (H, W)，值为 0 或 1

# 创建一个新的 RGBA 图像，形状为 (H, W, 4)
height, width = mask.shape
output_image = np.zeros((height, width, 4), dtype=np.uint8)

# 将掩码中为 1 的数据设置为颜色 (200, 200, 200, 255)
output_image[mask == 1] = [200, 200, 200, 255]

# 将掩码中为 0 的数据设置为透明 (0, 0, 0, 0)
output_image[mask == 0] = [0, 0, 0, 0]

# 将 NumPy 数组转换为 PIL 图像
output_image_pil = Image.fromarray(output_image, mode="RGBA")

# 保存为 PNG 图像
output_image_pil.save("output_image.png")
```

### 代码解释：

1. **`np.load("watermark_mask.npy")`**：
   - 加载掩码文件，假设掩码是一个形状为 `(H, W)` 的 NumPy 数组，值为 `0` 或 `1`。
2. **`np.zeros((height, width, 4), dtype=np.uint8)`**：
   - 创建一个形状为 `(H, W, 4)` 的 NumPy 数组，用于存储 RGBA 图像数据。
3. **`output_image[mask == 1] = [200, 200, 200, 255]`**：
   - 将掩码中值为 `1` 的像素设置为颜色 `(200, 200, 200, 255)`（灰色，不透明）。
4. **`output_image[mask == 0] = [0, 0, 0, 0]`**：
   - 将掩码中值为 `0` 的像素设置为透明 `(0, 0, 0, 0)`。
5. **`Image.fromarray(output_image, mode="RGBA")`**：
   - 将 NumPy 数组转换为 PIL 图像，模式为 `RGBA`（包含透明度通道）。
6. **`output_image_pil.save("output_image.png")`**：
   - 将生成的图像保存为 PNG 文件。

### 输出：

- 生成的 PNG 图像中：
  - 掩码值为 `1` 的区域显示为灰色 `(200, 200, 200)`，不透明。
  - 掩码值为 `0` 的区域完全透明。

### 示例：

假设掩码文件 `watermark_mask.npy` 的内容如下：

```python
mask = np.array([
    [1, 0],
    [0, 1]
])
```

生成的 PNG 图像将是一个 2x2 的图像，左上角和右下角为灰色，其他区域透明。

保存的文件名为 `output_image.png`。
