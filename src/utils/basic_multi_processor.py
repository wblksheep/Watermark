import io
import sys
import glob
import numpy as np
from PIL import Image
import os
import yaml
import logging
from logging.handlers import QueueHandler, QueueListener
import multiprocessing as mp
from multiprocessing import Pool, cpu_count
# 移除全局listener变量，改为类封装
class LogSystem:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls.manager = mp.Manager()
            cls.log_queue = cls.manager.Queue()
            cls.listener = QueueListener(
                cls.log_queue,
                logging.FileHandler("watermark.log"),
                logging.StreamHandler()
            )
            cls.listener.start()
        return cls._instance

    def __del__(self):
        if mp.current_process().name == 'MainProcess':
            if hasattr(self, 'listener'):
                try:
                    self.listener.stop()
                except Exception:  # 防止二次错误
                    pass
    def shutdown(self):
        """显式关闭方法"""
        self.listener.stop()
        self.manager.shutdown()
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

def overlay_and_crop(base_image, npy_data):
    """叠加水印并裁剪"""
    # print(f"npy_data.shape = {npy_data.shape}")
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

def process_single_image(input_path, output_path, config, npy_data, quality=30):
    """处理单张图片"""
    # 获取当前进程的 logger
    logger = logging.getLogger(__name__)
    try:
        # 加载并预处理图片
        base_image = load_image(input_path)

        scale = config['output_height'] / base_image.height
        width = int(base_image.width * scale)
        base_image = base_image.resize((width, config['output_height']))
        if base_image.mode == "RGB":
            buffer = io.BytesIO()
            base_image.save(buffer, format="JPEG", quality=quality)
            buffer.seek(0)
            base_image = Image.open(buffer)
        else:
            # PNG 压缩（无损但有压缩级别）
            buffer = io.BytesIO()
            base_image.save(buffer, format="PNG", compress_level=int((100-quality)/10))  # 最高压缩级别
            buffer.seek(0)
            base_image = Image.open(buffer)
        np.resize(npy_data, (config['output_height'], config['output_height']))
        # 应用水印
        watermarked = overlay_and_crop(base_image, npy_data)


        if os.path.splitext(output_path)[1] in [".jpeg", ".jpg"]:
            watermarked = watermarked.convert("RGB")
        # 保存结果
        watermarked.save(output_path, quality=100)
        logger.info(f"Processed: {os.path.basename(input_path)}")
    except Exception as e:
        logger.exception(f"Error processing {input_path}: {str(e)}")
        raise




# 修改日志队列创建方式
def configure_main_logger():
    """使用Manager创建跨进程安全队列"""
    manager = mp.Manager()
    log_queue = manager.Queue()

    # 主日志处理器（文件和控制台）
    file_handler = logging.FileHandler("watermark.log")
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(processName)s - [%(levelname)s] - %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # 队列监听器（主进程专用）
    listener = QueueListener(log_queue, file_handler, stream_handler)
    listener.start()

    return log_queue

def worker_init(log_queue):
    """子进程日志初始化（每个子进程调用一次）"""
    # 获取当前进程的 logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 清除已有处理器，避免重复
    if logger.hasHandlers():
        logger.handlers.clear()

    # 添加队列处理器
    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)

def generate_watermark(input_folder, watermark_type, opacity, quality):
    # 初始化日志系统
    log_system = LogSystem()

    """批量生成水印"""
    # 加载配置
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)['watermark']

    # 初始化路径
    output_folder = os.path.join(input_folder, 'output')
    os.makedirs(output_folder, exist_ok=True)

    # 加载水印数据
    npy_path = f"{watermark_type}.npy"
    # npy_data = load_npy(npy_path) * (opacity/100.0)
    npy_data = load_npy(npy_path)


    # 获取图片文件列表
    supported_formats = ('*.jpg', '*.jpeg', '*.png')
    image_files = []
    for fmt in supported_formats:
        image_files.extend(glob.glob(os.path.join(input_folder, fmt), recursive=True))

    with mp.Pool(
        processes=mp.cpu_count(),
        initializer=worker_init,
        initargs=(log_system.log_queue,)
    ) as pool:
        tasks = [(input_path, os.path.join(output_folder, os.path.basename(input_path)),
                config, npy_data, quality)
               for input_path in image_files]
        pool.starmap(process_single_image_wrapper, tasks)
    # 停止监听器
    listener.stop()

def process_single_image_wrapper(*arg):
    return process_single_image(*arg)

if __name__ == "__main__":
    # 加载配置
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)['watermark']
    input_folder = config['input_folder']
    watermark_type = config['npy_path']
    opacity = float(config['opacity'])
    quality = int(config['quality'])

    generate_watermark(input_folder, watermark_type, opacity, quality=quality)
