from pathlib import Path

from pydantic import validate_arguments
from functools import wraps

from src.config_loader.config_loader import ConfigLoader
from src.factory.processor_factory import ProcessorFactory
from src.models.config_loader.config_loader import YamlWatermarkConfig
from src.models.interfaces.impl.normal_processor import NormalWatermarkProcessor
import logging
logger = logging.getLogger(__name__)

class WatermarkModel:
    def __init__(self):
        self.config = ConfigLoader.load_watermark_config()
        self.processor_factory = ProcessorFactory(self.config)
        self._build_handlers()

    def get_watermark_config(self):
        return self.config

    def get_handler(self, wm_type):
        return getattr(self, self.config.config[wm_type]['handler'])

    def process_normal_watermark(self, folder,  **kwargs):
        # print({'folder':folder, **kwargs})
        """根据类型处理文件"""
        processor = self.processor_factory.create_processor("normal")
        # # 执行批量处理
        # input_dir = Path("input")
        output_dir = self._prepare_output_dir()
        return processor.process_batch(folder, output_dir, **kwargs)
        # processor = self.processor_factory.create_normal_processor()
        # # # 执行批量处理
        # # input_dir = Path("input")
        # output_dir = self._prepare_output_dir()
        # return processor.process_batch(folder, output_dir)

    def _prepare_output_dir(self) -> Path:
        """创建输出目录（复用逻辑）"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        return output_dir

    def process_foggy_watermark(self, folder, text="BH", **kwargs):
        """根据类型处理文件"""
        processor = self.processor_factory.create_processor("foggy")
        # # 执行批量处理
        # input_dir = Path("input")
        output_dir = self._prepare_output_dir()
        return processor.process_batch(folder, output_dir)
        # processor = self.processor_factory.create_foggy_processor()
        # # # 执行批量处理
        # # input_dir = Path("input")
        # output_dir = self._prepare_output_dir()
        # return processor.process_batch(folder, output_dir)





    def load_watermark_config(self):
        return self.config


    def _build_handlers(self):

        """动态创建带验证的处理方法"""
        for wm_type in self.config.config:
            handler_name = self.config.config[wm_type]['handler']
            original_method = getattr(self, handler_name)

            # 生成参数约束规则
            param_rules = {
                param: {'type': info['type'], **info.get('validations', {})}
                for param, info in self.config.config[wm_type]['params'].items()
            }

            # 立即绑定当前作用域的wm_type
            current_type = wm_type  # 创建局部变量副本

            # 使用闭包工厂函数
            def create_validator(wm_type, original_method):
                @wraps(original_method)
                def wrapper(folder, *args, **kwargs):
                    sanitized = self._sanitize_params(wm_type, kwargs)
                    return original_method(folder, *args, **sanitized)

                return wrapper

            wrapper = create_validator(wm_type, original_method)

            setattr(self, handler_name, wrapper)

    def _sanitize_params(self, wm_type, raw_params):
        """参数清洗与验证"""
        valid_params = {}
        for param, config in self.config.config[wm_type]['params'].items():
            # 必填校验
            if config.get('required') and param not in raw_params:
                raise ValueError(f"缺少必要参数: {param}")

            # 类型转换
            value = raw_params.get(param, config['default'])
            try:
                valid_params[param] = self._cast_type(value, config['type'])
            except Exception as e:
                raise ValueError(f"参数 {param} 类型错误: {str(e)}")

            # 范围校验
            if 'options' in config:
                param_type = config.get('type', 'str')
                input_value = valid_params[param]

                def validate_option(item):
                    """嵌套函数用于复用校验逻辑"""
                    if item not in str(config['options']).lower():
                        raise ValueError(
                            f"参数 {param} 值 '{item}' 无效，允许的选项: {config['options']}"
                        )

                # 处理列表类型参数
                if 'list' in param_type or isinstance(input_value, (list, tuple)):
                    if not isinstance(input_value, (list, tuple)):
                        input_value = [input_value]  # 统一转为可迭代对象

                    for item in input_value:
                        validate_option(str(item).lower())  # 支持大小写不敏感
                else:
                    validate_option(str(input_value).lower())
                # if valid_params[param] not in config['options']:
                #     raise ValueError(f"参数 {param} 值不在允许范围内")
            if 'min' in [param for param in config] and valid_params[param] < config['min']:
                raise ValueError(f"参数 {param} 值小于最小值 {config['min']}")
            if 'max' in [param for param in config] and valid_params[param] > config['max']:
                raise ValueError(f"参数 {param} 值大于最大值 {config['max']}")

        return valid_params

    def _cast_type(self, value, target_type):
        """安全类型转换"""
        type_map = {
            'int': int,
            'str': str,
            'float': float,
            'bool': lambda v: str(v).lower() in ['true', '1', 'yes'],
            'list[str]': lambda v: [s.strip() for s in str(v).split(',')]
            # 'check'
        }
        return type_map[target_type](value)

if __name__ == "__main__":
    # 测试代码
    model = WatermarkModel()
    # print(model.config)
    for wm_type in model.config:
        # 检查闭包变量
        handler = model.get_handler(wm_type)
        handler('', **{'allowed_formats': 'jpg', 'default_opacity': -1})
        # print([cell.cell_contents for cell in handler.__closure__])
        # 期望输出包含: 'normal', 原始方法引用等
        # handler = model.get_handler(wm_type)
        # print(f"Handler {wm_type} 绑定的类型: {handler.__name__}")
    # 期望输出:
    # Handler normal 绑定的类型: normal
    # Handler foggy 绑定的类型: foggy
