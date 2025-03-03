import numpy as np
from PIL import Image
import os
import yaml

# 读取图片文件
def load_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件 {image_path} 不存在")
    return Image.open(image_path)

# 读取npy文件
def load_npy(npy_path):
    if not os.path.exists(npy_path):
        raise FileNotFoundError(f"npy文件 {npy_path} 不存在")
    return np.load(npy_path)

# 将npy数据覆盖到图片上，并裁剪超出部分
def overlay_and_crop(base_image, npy_data):
    # # 将npy数据转换为PIL图像
    # npy_data = (npy_data * 255).astype(np.uint8)  # 假设npy数据在[0, 1]范围内
    watermark_image = Image.fromarray(npy_data)

    # 获取图片和水印的尺寸
    base_width, base_height = base_image.size
    watermark_width, watermark_height = watermark_image.size

    # 裁剪水印超出图片的部分
    if watermark_width > base_width or watermark_height > base_height:
        watermark_image = watermark_image.crop((0, 0, base_width, base_height))

    # 将水印覆盖到图片的左上角
    base_image.paste(watermark_image, (0, 0), watermark_image)  # 使用alpha通道（如果存在）
    return base_image

# 主函数
def main(input_image_path):
    # 打开并读取YAML文件
    with open('config.yaml', 'r') as file:
        # 加载并解析YAML内容
        config = yaml.safe_load(file)
    # 输入文件路径
    # input_image_path = "input.png"  # 可以是input.jpg、input.jpeg或input.png
    spacing = config['spacing']
    output_width = config['crop']['output_width']
    npy_path = f"watermark_image_{spacing}.npy"

    # 加载图片和npy文件
    try:
        base_image = load_image(input_image_path)
        npy_data = load_npy(npy_path)
    except FileNotFoundError as e:
        print(e)
        return
    scale = 2000 / base_image.height 
    width = int(base_image.width * scale)
    base_image = base_image.resize((width, 2000))

    # 将水印覆盖到图片上，并裁剪超出部分
    result_image = overlay_and_crop(base_image, npy_data)
    scale = output_width / 2000
    width = int(base_image.width * scale)
    result_image=result_image.resize((width, output_width))

    # 保存结果
    result_image.save(f"output{input_image_path[-4:]}", quality=95)
    print(f"处理完成，结果已保存为 output{input_image_path[-4:]}")

if __name__ == "__main__":
    main("input.png")
    main("input.jpg")