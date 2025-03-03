from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

def create_contrast_demo(original_rgb, adjusted_rgb, contrast_ratio):
    # 创建画布
    img = Image.new('RGB', (600, 300), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 绘制色块
    draw.rectangle([20, 20, 280, 280], fill=original_rgb)
    draw.rectangle([320, 20, 580, 280], fill=adjusted_rgb)

    # 添加文字说明
    font = ImageFont.truetype("arial.ttf", 18)
    draw.text((50, 285), f"Original\nL={calculate_luminance(*original_rgb):.3f}",
             font=font, fill=(0,0,0))
    draw.text((370, 285), f"Adjusted\nL={calculate_luminance(*adjusted_rgb):.3f}",
             font=font, fill=(0,0,0))
    draw.text((200, 130), f"Contrast Ratio: {contrast_ratio:.1f}:1",
             font=font, fill=(0,0,0))

    # 添加WCAG标准标注
    wcag_aa = "✔️ Pass WCAG AA" if contrast_ratio >= 4.5 else "❌ Fail WCAG AA"
    wcag_aaa = "✔️ Pass WCAG AAA" if contrast_ratio >= 7 else "❌ Fail WCAG AAA"
    draw.text((150, 180), wcag_aa, font=font, fill=(0,0,0))
    draw.text((150, 210), wcag_aaa, font=font, fill=(0,0,0))

    return img

# 测试用例
test_cases = [
    ((30, 30, 30), 0.175),   # 深灰色
    ((0, 100, 0), 0.15),     # 深绿色
    ((200, 50, 50), 0.12)    # 暗红色
]

def srgb_to_linear(channel):
    """将sRGB颜色通道值转换为线性RGB值。"""
    if channel <= 0.04045:
        return channel / 12.92
    else:
        return ((channel + 0.055) / 1.055) ** 2.4

def calculate_luminance(r, g, b):
    """计算sRGB颜色的相对亮度（WCAG标准）。"""
    # 将0-255的通道值归一化到0-1
    r_normalized = r / 255.0
    g_normalized = g / 255.0
    b_normalized = b / 255.0

    # 伽马校正
    r_linear = srgb_to_linear(r_normalized)
    g_linear = srgb_to_linear(g_normalized)
    b_linear = srgb_to_linear(b_normalized)

    # 计算亮度
    return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

def calculate_contrast(l1, l2):
    """计算两个亮度值的对比度。"""
    l1, l2 = sorted((l1, l2), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)

def adjust_color_to_target_luminance(r, g, b, target_luminance):
    """
    调整颜色使其达到目标亮度。
    返回调整后的RGB颜色（整数元组）。
    """
    # 当前亮度
    current_lum = calculate_luminance(r, g, b)
    if current_lum >= target_luminance:
        return (r, g, b)

    # 二分法寻找最小调整比例t
    low, high = 0.0, 1.0
    epsilon = 0.0001
    for _ in range(100):
        mid = (low + high) / 2
        # 混合颜色
        new_r = r + mid * (255 - r)
        new_g = g + mid * (255 - g)
        new_b = b + mid * (255 - b)
        # 计算亮度
        new_lum = calculate_luminance(new_r, new_g, new_b)
        if new_lum < target_luminance:
            low = mid
        else:
            high = mid
        if high - low < epsilon:
            break

    # 计算最终颜色
    t = high
    new_r = int(round(r + t * (255 - r)))
    new_g = int(round(g + t * (255 - g)))
    new_b = int(round(b + t * (255 - b)))
    # 确保值在0-255范围内
    new_r = max(0, min(255, new_r))
    new_g = max(0, min(255, new_g))
    new_b = max(0, min(255, new_b))
    return (new_r, new_g, new_b)

# 示例：调整深灰色使其亮度达到0.175
original_color = (30, 30, 30)
adjusted_color = adjust_color_to_target_luminance(*original_color, 0.175)
print("Adjusted Color:", adjusted_color)

# 生成对比图
results = []
for color, target in test_cases:
    adjusted = adjust_color_to_target_luminance(*color, target)
    l1 = calculate_luminance(*adjusted)
    l2 = calculate_luminance(*color)
    ratio = calculate_contrast(l1, l2)
    results.append(create_contrast_demo(color, adjusted, ratio))

# 显示结果（实际使用时需保存图片）
plt.figure(figsize=(15, 8))
for i, img in enumerate(results, 1):
    plt.subplot(1, 3, i)
    plt.imshow(img)
    plt.axis('off')
plt.tight_layout()
plt.show()