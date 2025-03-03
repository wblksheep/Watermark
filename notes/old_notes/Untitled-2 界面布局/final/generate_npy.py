from PIL import Image, ImageDraw, ImageFont, ImageFilter
import matplotlib.pyplot as plt
import numpy as np
import yaml

def find_intersection(line1, line2):
    # 提取线段端点
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    # 计算分母
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    # 如果分母为0，说明线段平行
    if denominator == 0:
        print("线段平行，无交点")
        return None

    # 计算交点
    numerator_x = (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
    numerator_y = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
    intersection_x = numerator_x / denominator
    intersection_y = numerator_y / denominator

    # 检查交点是否在线段上
    def is_point_on_line(x, y, line):
        x1, y1, x2, y2 = line
        # 检查点是否在线段的边界框内
        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            # 检查点是否在直线上
            cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
            if abs(cross) < 1e-12:  # 允许一定的浮点误差
                return True
        return False

    if is_point_on_line(intersection_x, intersection_y, line1) and is_point_on_line(intersection_x, intersection_y, line2):
        print(f"交点坐标: ({intersection_x}, {intersection_y})")
        return (intersection_x, intersection_y)
    else:
        print("交点不在线段上")
        return None
    
def plot_lines_and_intersection(line1, line2):
    # 提取线段端点
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    # 绘制线段
    plt.plot([x1, x2], [y1, y2], label='Line 1')
    plt.plot([x3, x4], [y3, y4], label='Line 2')

    # 查找交点
    intersection = find_intersection(line1, line2)

    # 如果存在交点，绘制交点
    if intersection:
        plt.scatter(*intersection, color='red', label='Intersection')

    # 设置图形属性
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Line Intersection')
    plt.legend()
    plt.grid(True)
    plt.show()



def draw_dashed_line(draw, start, end, color, shadow_color, dash_length=10, gap_length=5, width=2, offset=2, negtive=False):
    """
    绘制虚线
    :param draw: ImageDraw对象
    :param start: 起点坐标 (x1, y1)
    :param end: 终点坐标 (x2, y2)
    :param color: 线的颜色
    :param dash_length: 虚线段的长度
    :param gap_length: 虚线间隔的长度
    :param width: 线的宽度
    """
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    distance = (dx**2 + dy**2)**0.5
    dx_unit = dx / distance
    dy_unit = dy / distance
    
    # offset = offset if negtive else -offset
    negtive_1 = 1 if negtive else -1

    current_distance = 0
    while current_distance < distance:
        next_distance = current_distance + dash_length
        if next_distance > distance:
            next_distance = distance
            
        # draw.line(
        #     [(x1 + dx_unit * current_distance-offset, y1 + dy_unit * current_distance-negtive_1*offset),
        #      (x1 + dx_unit * next_distance-offset, y1 + dy_unit * next_distance-negtive_1*offset)],
        #     fill=shadow_color, width=2
        # )
        draw.line(
            [(x1 + dx_unit * current_distance, y1 + dy_unit * current_distance),
             (x1 + dx_unit * next_distance, y1 + dy_unit * next_distance)],
            fill=shadow_color, width=width+10
        )
        # draw.line(
        #     [(x1 + dx_unit * current_distance+offset, y1 + dy_unit * current_distance+negtive_1*offset),
        #      (x1 + dx_unit * next_distance+offset, y1 + dy_unit * next_distance+negtive_1*offset)],
        #     fill=shadow_color, width=2
        # )
        draw.line(
            [(x1 + dx_unit * current_distance, y1 + dy_unit * current_distance),
             (x1 + dx_unit * next_distance, y1 + dy_unit * next_distance)],
            fill=color, width=width
        )
        # draw.line(
        #     [(x1 + dx_unit * current_distance-offset, y1 + dy_unit * current_distance+offset),
        #      (x1 + dx_unit * next_distance-offset, y1 + dy_unit * next_distance+offset)],
        #     fill=(0,0,0,128), width=2
        # )
        # draw.line(
        #     [(x1 + dx_unit * current_distance-offset, y1 + dy_unit * current_distance+offset),
        #      (x1 + dx_unit * next_distance-offset, y1 + dy_unit * next_distance+offset)],
        #     fill=(0,0,0,128), width=2
        # )
        # draw.line(
        #     [(x1 + dx_unit * current_distance, y1 + dy_unit * current_distance),
        #      (x1 + dx_unit * next_distance, y1 + dy_unit * next_distance)],
        #     fill=color, width=width
        # )

        current_distance += dash_length + gap_length

angle_45 = []
angle_135= []

def draw_watermark_lines(image, angle, color, shadow_color, dash_length=10, line_width=6, spacing=50, emboss=True):
    """
    在图片上绘制指定角度的水印线
    :param image: PIL图片对象
    :param angle: 线的角度（45度或135度）
    :param color: 线的颜色
    :param spacing: 线之间的间距
    :param emboss: 是否添加凹陷特效
    """
    width, height = image.size
    draw = ImageDraw.Draw(image)
    index = 0
    if angle == 45:
        # pass
        # # 45度线：从左上到右下
        for i in range(-height, width, spacing):
        #     if emboss:
        #         # 绘制凹陷特效（暗色线）
        #         dark_color = (0, 0, 0, 128)  # 半透明黑色
        #         draw_dashed_line(draw, (i, 0), (i + height + 2, height + 2), dark_color, width=2)
        #         # 绘制凹陷特效（亮色线）
        #         light_color = (0, 0, 0, 128)  # 半透明白色
        #         draw_dashed_line(draw, (i, 0), (i + height - 2, height - 2), light_color, width=2)
        #     # 绘制主虚线
            draw_dashed_line(draw, (i, 0), (i + height, height), color,shadow_color,dash_length=dash_length, width=line_width, negtive=False)
            if index%2==0:
                angle_45.append((i, 0, i + height, height))
            index+=1
            
    elif angle == 135:
        # 135度线：从右上到左下
        for i in range(0, width + height, spacing):
            # if emboss:
                # # 绘制凹陷特效（暗色线）
                # dark_color = (0, 0, 0, 128)  # 半透明黑色
                # draw_dashed_line(draw, (i, 0), (i - height, height), dark_color, width=2)
                # # 绘制凹陷特效（亮色线）
                # light_color = (0, 0, 0, 128)  # 半透明白色
                # draw_dashed_line(draw, (i, 0), (i - height, height), light_color, width=2)
            # 绘制主虚线
            draw_dashed_line(draw, (i, 0), (i - height, height), color,shadow_color,dash_length=dash_length, width=line_width, negtive=True)
            if index%2==0:
                angle_135.append((i, 0, i - height, height))
            index+=1
def draw_foggy(image, angle, color, line_width=6, spacing=50):
    """
    在图片上绘制指定角度的水印线
    :param image: PIL图片对象
    :param angle: 线的角度（45度或135度）
    :param color: 线的颜色
    :param spacing: 线之间的间距
    :param emboss: 是否添加凹陷特效
    """
    width, height = image.size
    draw = ImageDraw.Draw(image)
    if angle == 45:
        for i in range(-height, width, spacing):
            draw.line(
            [(i, 0),
             (i + height, height)],
            fill=color, width=line_width
            )
    elif angle == 135:
        # 135度线：从右上到左下
        for i in range(0, width + height, spacing):
            draw.line(
            [(i, 0),
             (i - height, height)],
            fill=color, width=line_width
            )

def main():

    # 打开并读取YAML文件
    with open('config.yaml', 'r') as file:
        # 加载并解析YAML内容
        config = yaml.safe_load(file)
    # 创建一个空白图片
    width, height = 6000, 6000
    background_color = (255, 255, 255, 0)  # 纯白色背景
    image = Image.new('RGBA', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    image_foggy = Image.new('RGBA', (width, height), background_color)
    watermark_text = 'BH'
    spacing = config['spacing']
    opacity = config['opacity']
    shadow_opacity = config['shadow_opacity']
    opacity = int(opacity/100*255)
    shadow_opacity = int(shadow_opacity/100*255)
    line_width = config['line_width']
    foggy_line_width = config['foggy_line_width']
    dash_length = config['dash_length']
    color = (200, 200, 200, opacity)
    shadow_color = (200,200, 200, shadow_opacity)
    # 设置字体和大小
    font = ImageFont.truetype('arial.ttf', 60)
    # 绘制45度水印线
    draw_watermark_lines(image, angle=45, color=color, shadow_color=shadow_color, dash_length=dash_length, spacing=spacing, emboss=True, line_width=line_width)  # 白色半透明
    # draw_watermark_lines(image, angle=45, color=(255, 0, 0, opacity), shadow_color=shadow_color, spacing=spacing, emboss=True, line_width=line_width)  # 白色半透明
    # draw_foggy(image_foggy,angle=45,color=color,line_width=foggy_line_width, spacing=spacing)

    # 绘制135度水印线
    # draw_watermark_lines(image, angle=135, color=(255, 255, 255, 128), spacing=50, emboss=True)  # 红色半透明
    draw_watermark_lines(image, angle=135, color=color, shadow_color=shadow_color, dash_length=dash_length, spacing=spacing, emboss=True, line_width=line_width)  # 白色半透明
    # draw_watermark_lines(image, angle=135, color=(0, 0, 255, opacity), shadow_color=shadow_color, spacing=spacing, emboss=True, line_width=line_width)  # 白色半透明
    # draw_foggy(image_foggy,angle=135,color=color,line_width=foggy_line_width, spacing=spacing)
    intersections = []
    # 计算所有交点
    for i in range(len(angle_135)):
        for j in range(len(angle_45)):
            # 示例线段
            line1 = angle_135[i]
            line2 = angle_45[j]
            intersection = find_intersection(line1, line2)

            # # 绘制线段和交点
            # plot_lines_and_intersection(line1, line2)
            if intersection:
                intersections.append(intersection)
                x=intersection[0]
                y=intersection[1]
                # plt.scatter(intersection[0], intersection[1], color="red", zorder=5)
                # 获取文本的边界框
                bbox = draw.textbbox((0, 0), watermark_text, font=font)

                # 计算文本的宽度和高度
                text_width = bbox[2] - bbox[0]  # right - left
                text_height = bbox[3] - bbox[1]  # bottom - top
                x =x-text_width/2
                y=y-text_height/2
                draw.text((x + 2, y + 2), watermark_text, font=font, fill=shadow_color)
                draw.text((x - 2, y - 2), watermark_text, font=font, fill=shadow_color)
                draw.text((x - 2, y + 2), watermark_text, font=font, fill=shadow_color)
                draw.text((x + 2, y - 2), watermark_text, font=font, fill=shadow_color)
                draw.text((x, y), watermark_text, font=font, fill=shadow_color)
    # # 显示图片
    # plt.imshow(image)
    # plt.title("image")
    # plt.axis('off')  # 隐藏坐标轴
    # plt.show()  
    # blurred_image = image.filter(ImageFilter.GaussianBlur(radius=10))
    blurred_image = image_foggy.filter(ImageFilter.GaussianBlur(radius=20))
    # # 显示图片
    # plt.imshow(blurred_image)
    # plt.title("blurred_image")
    # plt.axis('off')  # 隐藏坐标轴
    # plt.show()
    


    # 将模糊后的图像与原始图像叠加
    final_image = Image.alpha_composite(image, blurred_image)
    # # 显示图片
    # plt.imshow(final_image)
    # plt.title("45度和135度虚线水印（凹陷特效）")
    # plt.axis('off')  # 隐藏坐标轴
    # plt.show()
    
    rotated_np = np.array(final_image)
    # 提取 alpha 通道（第 4 个通道）
    alpha_channel = rotated_np[:,:,3]
    # 创建掩码：alpha 为 0 的点设为 0，其他点设为 1
    mask = np.where(alpha_channel==0,0,1).astype(np.uint8)
    # 保存掩码为 .npy 文件
    np.save(f"watermark_mask_{spacing}.npy", mask)
    print(f"水印图片已保存为 watermark_mask_{spacing}.npy", mask)
    
    # 将掩码转换为 PIL 图像
    mask_image = Image.fromarray(mask*255, mode="L") # 将 0/1 映射为 0/255
    # 保存掩码为 PNG 图像
    mask_image.save(f"watermark_mask_{spacing}.png")
    print(f"水印图片已保存为 watermark_mask_{spacing}.png", mask)

if __name__ == "__main__":
    main()