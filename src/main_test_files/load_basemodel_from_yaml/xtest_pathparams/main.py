from pathlib import Path
from pydantic import ValidationError, BaseModel
import yaml
import pytest

class PathParams(BaseModel):
    output_dir: Path

class ProcessorParams(BaseModel):
    opacity: float = 0.8
    output_dir: PathParams

def load_test_cases():
    """加载 YAML 测试配置"""
    with open("test_params.yml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        return [
            pytest.param(
                case["input"],
                case["should_fail"],
                id=case["description"]
            )
            for case in config["test_cases"]
        ]

@pytest.mark.parametrize("input_data,should_fail", load_test_cases())
def test_processor_params(input_data, should_fail):
    """参数化测试主逻辑"""
    try:
        # 处理嵌套路径转换
        if "output_dir" in input_data:
            input_data["output_dir"] = Path(input_data["output_dir"])

        params = ProcessorParams(**input_data)

        # 验证不应失败的用例
        assert not should_fail, "预期验证失败但通过了"

        # 类型校验
        assert isinstance(params.opacity, float)
        assert isinstance(params.output_dir.output_dir, Path)

        # 值范围校验
        if "opacity" in input_data:
            assert 0 <= params.opacity <= 1

    except ValidationError as e:
        # 验证应失败的用例
        assert should_fail, f"意外失败: {e}"

        # 错误类型校验
        errors = e.errors()
        assert len(errors) > 0

        # 检查嵌套路径错误
        if "output_dir" in input_data.get("output_dir", {}):
            assert any(
                error["loc"] == ("output_dir", "output_dir")
                for error in errors
            )