对图像柔光处理的代码是怎么实现的？

------------- v3

图像柔光处理是一种常见的图像处理技术，可以使图像看起来更加柔和、温暖。柔光效果通常通过将图像与自身进行某种混合操作来实现。以下是一个使用 Python 和 OpenCV 库实现柔光处理的示例代码：

```python
import cv2
import numpy as np

def soft_light_blend(img1, img2):
    # 柔光混合公式
    result = np.where(img2 <= 128,
                      img1 * img2 / 128.0,
                      255 - (255 - img1) * (255 - img2) / 128.0)
    return np.clip(result, 0, 255).astype(np.uint8)

def apply_soft_light(image, intensity=0.5):
    # 将图像归一化到0-1范围
    image = image.astype(np.float32) / 255.0

    # 创建一个与图像大小相同的柔光层
    soft_light_layer = np.ones_like(image) * intensity

    # 应用柔光混合
    blended_image = soft_light_blend(image, soft_light_layer)

    # 将图像恢复到0-255范围
    blended_image = (blended_image * 255).astype(np.uint8)

    return blended_image

# 读取图像
image = cv2.imread('input_image.jpg')

# 应用柔光处理
soft_light_image = apply_soft_light(image, intensity=0.5)

# 保存结果
cv2.imwrite('soft_light_image.jpg', soft_light_image)

# 显示结果
cv2.imshow('Soft Light Image', soft_light_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

### 代码说明：

1. **soft_light_blend 函数**：实现了柔光混合的公式。根据像素值的大小，使用不同的混合方式。

   - 如果 `img2` 的像素值小于等于 128，则使用 `img1 * img2 / 128.0`。
   - 否则，使用 `255 - (255 - img1) * (255 - img2) / 128.0`。

2. **apply_soft_light 函数**：将图像与柔光层进行混合。`intensity` 参数控制柔光的强度。

3. **图像读取与保存**：使用 OpenCV 读取图像，并保存处理后的图像。

### 参数调整：

- `intensity`：控制柔光的强度，取值范围为 0 到 1。值越大，柔光效果越明显。

### 注意事项：

- 代码中的 `soft_light_blend` 函数假设输入图像已经归一化到 0-1 范围。
- 如果图像是彩色图像，代码会自动对每个通道进行处理。

### 依赖库：

- `OpenCV`：用于图像读取、显示和保存。
- `NumPy`：用于数值计算和数组操作。

你可以根据需要调整代码中的参数，以获得不同的柔光效果。
