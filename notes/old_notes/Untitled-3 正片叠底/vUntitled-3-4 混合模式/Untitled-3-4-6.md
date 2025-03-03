watermark = watermark.point(lambda p: int(p * 0.5)) # 50% 透明度
这里的问题是对每个点的所有通道都*0.5，而应该只对 alpha 通道\*0.5，要修改的。

---- v3

你提到的代码确实是对图像的所有通道（包括 RGB 通道）都乘以 0.5，而实际上只需要对 **alpha 通道**（透明度通道）进行操作。为了实现这一点，我们需要将图像转换为带有 alpha 通道的模式（如 `RGBA`），然后仅对 alpha 通道进行调整。

以下是修改后的代码：

```python
from PIL import Image

# 假设 watermark 是一个 PIL 图像对象
watermark = watermark.convert("RGBA")  # 确保图像是 RGBA 模式（带有 alpha 通道）

# 分离图像的通道
r, g, b, a = watermark.split()

# 仅对 alpha 通道进行调整
a = a.point(lambda p: int(p * 0.5))  # 将 alpha 通道的透明度设置为 50%

# 重新合并通道
watermark = Image.merge("RGBA", (r, g, b, a))
```

### 解释：

1. **`convert("RGBA")`**：将图像转换为 RGBA 模式，确保它有 alpha 通道。
2. **`split()`**：将图像的四个通道（R、G、B、A）分离。
3. **`a.point(lambda p: int(p * 0.5))`**：仅对 alpha 通道的每个像素值乘以 0.5，实现 50% 的透明度。
4. **`Image.merge("RGBA", (r, g, b, a))`**：将调整后的 alpha 通道与原始 RGB 通道重新合并。

这样修改后，只有 alpha 通道的透明度会被调整，而 RGB 通道的值保持不变。
