from pathlib import Path
from config_loader.config_loader import YamlWatermarkConfig
from interfaces.impl.normal_processor import NormalWatermarkProcessor

def main():
    # 初始化配置
    config = YamlWatermarkConfig(Path("config.yaml"))

    # 创建处理器
    processor = NormalWatermarkProcessor(
        config=config,
        npy_path="normal.npy"
    )
    try:
        # 执行批量处理
        input_dir = Path("input")
        output_dir = Path("output")
        success_files = processor.process_batch(input_dir, output_dir)
        # 执行批量处理
        input_dir = Path("input")
        output_dir = Path("output2")
        success_files = processor.process_batch(input_dir, output_dir)
    except Exception as e:
        processor.logger.exception(e)
    finally:
        processor.log_system.shutdown()

    print(f"成功处理 {len(success_files)} 张图片")

if __name__ == "__main__":
    main()