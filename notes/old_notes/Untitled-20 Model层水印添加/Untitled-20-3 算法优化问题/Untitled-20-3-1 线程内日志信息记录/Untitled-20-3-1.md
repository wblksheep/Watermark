添加线程日志的方法是什么？

```python
    # 批量处理
    with Pool(processes=cpu_count()) as pool:
        logger = logging.getLogger(__name__)
        pool.starmap(process_single_image_wrapper,
                     [(input_path, os.path.join(output_folder, os.path.basename(input_path)), config, npy_data,
                       quality)
                      for input_path in image_files])
```

---R1

在多进程环境下实现线程/进程日志的统一记录，需要通过 **队列（Queue）** 将子进程的日志传递到主进程处理。以下是具体实现方法：

---

### 一、配置日志队列和监听器（主进程）

```python
import logging
from logging.handlers import QueueHandler, QueueListener
import multiprocessing as mp

def configure_main_logger():
    """主进程日志配置（添加队列监听器）"""
    log_queue = mp.Queue()  # 多进程安全队列

    # 主日志处理器（文件和控制台）
    file_handler = logging.FileHandler("watermark.log")
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(processName)s - [%(levelname)s] - %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # 队列监听器（主进程专用）
    global listener
    listener = QueueListener(log_queue, file_handler, stream_handler)
    listener.start()

    return log_queue
```

---

### 二、子进程日志初始化

```python
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
```

---

### 三、修改多进程池调用代码

```python
def generate_watermark(...):
    # 初始化日志队列和监听器
    log_queue = configure_main_logger()

    # 创建进程池时初始化日志
    with mp.Pool(
        processes=mp.cpu_count(),
        initializer=worker_init,
        initargs=(log_queue,)
    ) as pool:
        tasks = [(input_path, os.path.join(output_folder, os.path.basename(input_path)),
                config, npy_data, quality)
               for input_path in image_files]
        pool.starmap(process_single_image, tasks)

    # 停止监听器
    listener.stop()
```

---

### 四、在子进程函数中记录日志

```python
def process_single_image(input_path, output_path, config, npy_data, quality):
    """处理单张图片（子进程内）"""
    # 获取当前进程的 logger
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"开始处理: {input_path}")
        # ...原有处理逻辑...
        logger.info(f"完成处理: {output_path}")
    except Exception as e:
        logger.error(f"处理失败: {input_path}, 错误: {str(e)}", exc_info=True)
        raise
```

---

### 五、日志格式说明

生成的日志会包含 **进程名称**，便于区分不同子进程：

```log
2023-10-01 12:00:00 - ForkPoolWorker-1 - [INFO] - 开始处理: /input/image1.jpg
2023-10-01 12:00:02 - ForkPoolWorker-2 - [INFO] - 完成处理: /output/image2.jpg
```

---

### 六、注意事项

1. **避免直接使用文件处理器**：子进程中不要直接添加 `FileHandler`，否则会导致多进程写文件冲突
2. **资源释放**：主进程结束时必须调用 `listener.stop()`
3. **异常传递**：如果使用 `starmap`，异常会传递到主进程，需在主函数外层包裹 try-except

---

通过这种方式，所有子进程的日志会通过队列统一到主进程处理，实现线程/进程安全的日志记录。
