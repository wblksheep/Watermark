from PIL import Image, ImageDraw, ImageFont, ImageChops
import random

def calculate_brightness(image, x, y, text_width, text_height):
    """计算指定区域的平均亮度"""
    region = image.crop((x, y, x + text_width, y + text_height))
    grayscale = region.convert("L")
    histogram = grayscale.histogram()
    brightness = sum(i * v for i, v in enumerate(histogram)) / (text_width * text_height)
    return brightness

def add_tiled_watermark(image, text, font_path="arial.ttf", font_size=30, spacing=100):
    """平铺水印，并根据背景亮度动态调整颜色"""
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0,0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    for x in range(0, image.width, text_width + spacing):
        for y in range(0, image.height, text_height + spacing):
            brightness = calculate_brightness(image, x, y, text_width, text_height)
            watermark_color = "black" if brightness > 127 else "white"
            draw.text((x, y), text, font=font, fill=watermark_color)
    return image

def add_scattered_watermark(image, text, font_path="arial.ttf", font_size=30, positions=None):
    """分散水印，并根据背景亮度动态调整颜色"""
    if positions is None:
        positions = [
            (10, 10),  # 左上
            (image.width - 150, 10),  # 右上
            (10, image.height - 50),  # 左下
            (image.width - 150, image.height - 50),  # 右下
            (image.width // 2 - 75, image.height // 2 - 25),  # 中心
        ]

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0,0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    for pos in positions:
        x, y = pos
        brightness = calculate_brightness(image, x, y, text_width, text_height)
        watermark_color = "black" if brightness > 127 else "white"
        draw.text((x, y), text, font=font, fill=watermark_color)

        region = image.crop((x, y, x + text_width, y + text_height))
        # 创建一张与图像大小相同的透明图像
        text_mask = Image.new("L", region.size, 0)  # 用于生成文本区域的掩码
        draw_opacity = ImageDraw.Draw(text_mask)

        # 在透明图像上绘制文本
        x_text, y_text = 0, 0  # 文本位置
        text = "Watermark"
        draw_opacity.text((x_text, y_text), text, font=font, fill=watermark_color)  # 用白色绘制文本

        # 提取文本覆盖区域的图像
        text_region = region.copy()
        text_region.putalpha(text_mask)  # 将文本区域作为透明度通道
        text_color = (0,0,0,128) if watermark_color=="black" else (0,0,0,128)
        # 创建文本颜色的图像
        text_color_image = Image.new("RGBA", region.size, text_color)  # 假设文本颜色
        text_color_image.putalpha(text_mask)  # 将文本区域作为透明度通道

        # 对文本覆盖区域的图像和文本颜色进行正片叠底
        multiplied_region = ImageChops.multiply(text_color_image, text_region.convert("RGBA"))

        # 将处理后的区域放回原图
        result_image = region.copy()
        image.paste(multiplied_region, (x, y), multiplied_region)

        # 保存或显示结果图像
        image.show()
        
    return image

def add_random_watermark(image, text, font_path="arial.ttf", font_size=30, num_watermarks=10):
    """随机分布水印，并根据背景亮度动态调整颜色"""
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0,0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    for _ in range(num_watermarks):
        x = random.randint(0, image.width - text_width)
        y = random.randint(0, image.height - text_height)
        brightness = calculate_brightness(image, x, y, text_width, text_height)
        watermark_color = "black" if brightness > 127 else "white"
        draw.text((x, y), text, font=font, fill=watermark_color)
    return image

# 示例
image = Image.open("input.jpg")

# # 平铺水印
# tiled_image = add_tiled_watermark(image, "Watermark")
# tiled_image.save("tiled_watermark.jpg")
# tiled_image.show()

# 分散水印
scattered_image = add_scattered_watermark(image, "Watermark")
scattered_image.save("scattered_watermark.jpg")
scattered_image.show()

# # 随机分布水印
# random_image = add_random_watermark(image, "Watermark")
# random_image.save("random_watermark.jpg")
# random_image.show()