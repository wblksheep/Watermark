from pathlib import Path
from pydantic import ValidationError, BaseModel
import yaml
import sys

class ProcessorParams(BaseModel):
    """参数基类（定义公共字段）"""
    opacity: float = 0.8
    output_dir: Path

def load_test_cases(config_path: Path) -> list:
    """加载 YAML 测试配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('test_cases', [])
    except FileNotFoundError:
        print(f"错误：配置文件 {config_path} 不存在")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"YAML 解析错误: {e}")
        sys.exit(1)

def convert_paths(test_case: dict) -> dict:
    """转换路径字符串为 Path 对象"""
    if 'output_dir' in test_case['input']:
        # 处理嵌套路径
        test_case['input']['output_dir'] = Path(
            str(test_case['input']['output_dir'])
        )
    return test_case

def run_test_case(case: dict):
    """执行单个测试用例"""
    print(f"\n=== 测试场景：{case['description']} ===")
    print(f"输入参数：{case['input']}")

    try:
        # 自动类型转换验证
        params = ProcessorParams(**case['input'])
        print("验证通过 ✅")
        print(f"生成参数对象：{params}")

        # 显示实际使用的值
        print("实际使用参数：")
        print(f"  - 透明度：{params.opacity} ({type(params.opacity)})")
        print(f"  - 输出目录：{params.output_dir} ({type(params.output_dir)})")

        # 验证路径类型转换
        if not isinstance(params.output_dir, Path):
            raise TypeError("路径类型转换失败")

    except (ValidationError, TypeError) as e:
        handle_validation_error(e, case)

def handle_validation_error(e: Exception, case: dict):
    """处理验证错误"""
    expected_failure = case.get('should_fail', False)

    if isinstance(e, ValidationError):
        errors = e.errors()
        error_msg = "预期失败 ✅" if expected_failure else "意外验证失败 ❌"
    else:
        errors = [{"loc": ("output_dir",), "msg": str(e)}]
        error_msg = "类型错误 ❌"

    print(error_msg)
    print("错误详情：")

    for error in errors:
        field = error['loc']
        print(f"  - 字段: {field}")
        print(f"    问题: {error['msg']}")
        print(f"    输入值: {case['input'].get(field, '未提供')}")

    if expected_failure and not isinstance(e, ValidationError):
        print("警告：预期验证失败但收到其他错误类型")

def main():
    # 加载测试配置
    test_cases = load_test_cases(Path("test_config.yml"))

    # 执行测试用例
    for case in test_cases:
        processed_case = convert_paths(case)
        run_test_case(processed_case)

if __name__ == "__main__":
    main()