import numpy as np
from PIL import Image, ImageChops
import os
import yaml

# 读取图片文件
def load_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件 {image_path} 不存在")
    return Image.open(image_path)

# 读取npy文件
def load_npy(npy_path, color):
    if not os.path.exists(npy_path):
        raise FileNotFoundError(f"npy文件 {npy_path} 不存在")
    mask = np.load(npy_path)
    height, width = mask.shape
    npy_data = np.zeros((height, width, 4), dtype=np.uint8)
    npy_data[mask==1] = color
    npy_data[mask==0] = [0,0,0,0]
    return npy_data

# 将npy数据覆盖到图片上，并裁剪超出部分
def overlay_and_crop(base_image, npy_data, final_opacity):
    # # 将npy数据转换为PIL图像
    # npy_data = (npy_data * 255).astype(np.uint8)  # 假设npy数据在[0, 1]范围内
    watermark_image = Image.fromarray(npy_data)

    # 获取图片和水印的尺寸
    base_width, base_height = base_image.size
    watermark_width, watermark_height = watermark_image.size

    # 裁剪水印超出图片的部分
    if watermark_width > base_width or watermark_height > base_height:
        watermark_image = watermark_image.crop((0, 0, base_width, base_height))
    '''
        算法：
            修改alpha通道透明度
    '''
    
    # 设置水印透明度
    # 假设 watermark 是一个 PIL 图像对象
    watermark_image = watermark_image.convert("RGBA")# 确保图像是 RGBA 模式（带有 alpha 通道）
    # 分离图像的通道
    r, g, b, a = watermark_image.split()
    
    # 仅对 alpha 通道进行调整
    a = a.point(lambda p: int(p * final_opacity))# 将 alpha 通道的透明度设置为 final_opacity%    
    
    # 重新合并通道
    watermark_image = Image.merge("RGBA", (r, g, b, a))    
        
    '''
        算法：此时将水印与底图正片叠底
    '''
    
    result = ImageChops.multiply(base_image, watermark_image)
    # result.show()
    
    

    
    # # 将水印覆盖到图片的左上角
    base_image.paste(result, (0, 0), result)  # 使用alpha通道（如果存在）
    # base_image = ImageChops.multiply(base_image, watermark_image)
    return base_image
    
    

# 主函数
def generate_watermark(input_image_path, npy_path, final_opacity=50):
    # 打开并读取YAML文件
    with open('config.yaml', 'r') as file:
        # 加载并解析YAML内容
        config = yaml.safe_load(file)
    # 输入文件路径
    # input_image_path = "input.png"  # 可以是input.jpg、input.jpeg或input.png
    spacing = config['spacing']
    output_width = config['crop']['output_width']
    color = config['color']
    # npy_path = f"watermark_mask_{spacing}.npy"
    npy_path = f"{npy_path}.npy"
    # final_opacity = config['final_opacity'] / 100.0
    final_opacity = final_opacity / 100.0

    # 加载图片和npy文件
    try:
        base_image = load_image(input_image_path).convert('RGBA')
        npy_data = load_npy(npy_path, color)
    except FileNotFoundError as e:
        print(e)
        return
    scale = 2000 / base_image.height 
    width = int(base_image.width * scale)
    base_image = base_image.resize((width, 2000))

    # 将水印覆盖到图片上，并裁剪超出部分
    result_image = overlay_and_crop(base_image, npy_data, final_opacity)
    scale = output_width / 2000
    width = int(base_image.width * scale)
    result_image=result_image.resize((width, output_width)).convert("RGB")

    # 保存结果
    # result_image.save(f"output{input_image_path[-5:]}", quality=95)
    

    result_image.convert("RGB")
    result_image.save(input_image_path.replace("input", "output"))
    # print(f"处理完成，结果已保存为 output{input_image_path[-5:]}")

if __name__ == "__main__":
    generate_watermark("input.png")
    generate_watermark("input.jpg")
    generate_watermark("input1.jpg")
    generate_watermark("input1.png")
    
    """
        算法：
            读取一个mask，将其中为1的数据设置为color: (200, 200, 200, 255)，将其中为0的数据设为透明
    
    
    """
    