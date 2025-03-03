对以下代码中 alpha 通道为 0 的点设为 0，其他点设为 1，作为掩码 mask 的 npy 数组：

```python
    rotated_np = np.array(final_image)  # 转换为 (H,W,4) 的uint8数组

    np.save(f"watermark_image_{spacing}.npy", rotated_np)
```

--- v3

要将 alpha 通道为 0 的点设为 0，其他点设为 1，并生成一个掩码 `mask` 的 `.npy` 数组，可以按照以下步骤修改代码：

### 修改后的代码：

```python
import numpy as np

# 假设 final_image 是一个 PIL 图像对象
rotated_np = np.array(final_image)  # 转换为 (H, W, 4) 的 uint8 数组

# 提取 alpha 通道（第 4 个通道）
alpha_channel = rotated_np[:, :, 3]

# 创建掩码：alpha 为 0 的点设为 0，其他点设为 1
mask = np.where(alpha_channel == 0, 0, 1).astype(np.uint8)

# 保存掩码为 .npy 文件
np.save(f"watermark_mask_{spacing}.npy", mask)
```

### 代码解释：

1. **`np.array(final_image)`**：将 PIL 图像转换为 NumPy 数组，形状为 `(H, W, 4)`，其中第 4 个通道是 alpha 通道。
2. **`alpha_channel = rotated_np[:, :, 3]`**：提取 alpha 通道。
3. **`np.where(alpha_channel == 0, 0, 1)`**：
   - 使用 `np.where` 函数，将 alpha 通道中值为 0 的点设为 0，其他点设为 1。
4. **`astype(np.uint8)`**：将掩码的数据类型转换为 `uint8`，确保保存为 `.npy` 文件时是整数格式。
5. **`np.save`**：将掩码保存为 `.npy` 文件。

### 输出：

- 生成的 `mask` 是一个形状为 `(H, W)` 的 NumPy 数组，其中：
  - 值为 `0` 表示 alpha 通道为 0（完全透明）。
  - 值为 `1` 表示 alpha 通道不为 0（不透明或部分透明）。
- 保存的文件名为 `watermark_mask_{spacing}.npy`，其中 `{spacing}` 是变量值。

