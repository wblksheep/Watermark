并保存为一个可视化的 png 图像
----- v3

为了将生成的掩码 `mask` 保存为一个可视化的 PNG 图像，可以将掩码数组转换为 PIL 图像并保存。以下是完整的代码：

### 修改后的代码：

```python
import numpy as np
from PIL import Image

# 假设 final_image 是一个 PIL 图像对象
rotated_np = np.array(final_image)  # 转换为 (H, W, 4) 的 uint8 数组

# 提取 alpha 通道（第 4 个通道）
alpha_channel = rotated_np[:, :, 3]

# 创建掩码：alpha 为 0 的点设为 0，其他点设为 1
mask = np.where(alpha_channel == 0, 0, 1).astype(np.uint8)

# 保存掩码为 .npy 文件
np.save(f"watermark_mask_{spacing}.npy", mask)

# 将掩码转换为 PIL 图像
mask_image = Image.fromarray(mask * 255, mode="L")  # 将 0/1 映射为 0/255

# 保存掩码为 PNG 图像
mask_image.save(f"watermark_mask_{spacing}.png")
```

### 代码解释：

1. **`np.where(alpha_channel == 0, 0, 1)`**：
   - 生成掩码数组，其中 alpha 通道为 0 的点设为 0，其他点设为 1。
2. **`Image.fromarray(mask * 255, mode="L")`**：
   - 将掩码数组（值为 0 或 1）乘以 255，映射为灰度图像（0 为黑色，255 为白色）。
   - `mode="L"` 表示生成单通道的灰度图像。
3. **`mask_image.save`**：
   - 将掩码图像保存为 PNG 文件，文件名为 `watermark_mask_{spacing}.png`。

### 输出：

- **`.npy` 文件**：`watermark_mask_{spacing}.npy`，保存掩码的 NumPy 数组。
- **`.png` 文件**：`watermark_mask_{spacing}.png`，保存掩码的可视化图像，其中：
  - 黑色区域表示 alpha 通道为 0（完全透明）。
  - 白色区域表示 alpha 通道不为 0（不透明或部分透明）。

### 示例：

假设 `final_image` 是一个带有透明区域的图像，生成的掩码 PNG 图像将清晰地显示透明区域（黑色）和非透明区域（白色）。
