from pydantic import ValidationError, BaseModel, Field, validator, field_validator
import random
import string
from pathlib import Path

class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: str = Field(min_length=3)
    port: int = Field(ge=1024, le=65535)
    timeout_sec: float = Field(10.0, description="连接超时时间(秒)")

class AlgorithmParams(BaseModel):
    """算法参数配置"""
    learning_rate: float = 0.001
    batch_size: int = 32
    use_gpu: bool = False

class AppConfig(BaseModel):
    """全局应用配置"""
    env: str = Field("dev", pattern="^(dev|test|prod)$")
    log_level: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")
    database: DatabaseConfig
    model_params: AlgorithmParams
    output_dir: Path = Path("results")

    # @field_validator("output_dir")
    # def validate_output_dir(cls, v):
    #     if not v.is_absolute():
    #         raise ValueError("输出路径必须为绝对路径")
    #     return v

def generate_test_case(case_type: str) -> dict:
    """生成不同类型的测试配置"""
    base_config = {
        "env": "dev",
        "log_level": "INFO",
        "database": {
            "host": "db.example.com",
            "port": 5432,
            "timeout_sec": 15.0
        },
        "model_params": {
            "learning_rate": 0.001,
            "batch_size": 32,
            "use_gpu": False
        },
        "output_dir": "/data/output"
    }

    # 生成随机字符串
    rand_str = lambda: ''.join(random.choices(string.ascii_lowercase, k=5))

    if case_type == "valid":
        return base_config

    elif case_type == "invalid_env":
        return {**base_config, "env": "invalid_env"}

    elif case_type == "invalid_port":
        return {
            **base_config,
            "database": {
                **base_config["database"],
                "port": random.choice([1023, 65536, "invalid"])
            }
        }

    elif case_type == "nested_error":
        return {
            **base_config,
            "model_params": {
                "learning_rate": "not_a_float",
                "batch_size": 10.5,  # 浮点数错误
                "use_gpu": "not_bool"
            }
        }

    elif case_type == "path_error":
        return {
            **base_config,
            "output_dir": "relative/path"
        }

    elif case_type == "random":
        return {
            "env": random.choice(["dev", "test", "prod", "invalid"]),
            "log_level": random.choice(["DEBUG", "INFO", "ERROR", "INVALID"]),
            "database": {
                "host": rand_str() * random.randint(1, 3),  # 可能触发长度校验
                "port": random.randint(0, 100000),
                "timeout_sec": "string_instead_of_float"
            },
            "model_params": {
                "learning_rate": random.choice([0.01, "invalid"]),
                "batch_size": random.choice([16, 32.0]),
                "use_gpu": random.choice([True, False, "yes"])
            },
            "output_dir": random.choice(["/valid/path", "invalid/relative"])
        }

def validate_config(config: dict) -> dict:
    """执行配置校验并返回结果"""
    try:
        parsed = AppConfig(**config)
        return {
            "valid": True,
            "config": parsed.dict(),
            "errors": None
        }
    except ValidationError as e:
        return {
            "valid": False,
            "config": None,
            "errors": [
                {
                    "field": "->".join(map(str, err["loc"])),
                    "message": err["msg"],
                    "input": get_nested_value(config, err["loc"])
                }
                for err in e.errors()
            ]
        }

def get_nested_value(data: dict, loc: tuple):
    """递归获取嵌套字段值"""
    for key in loc:
        if isinstance(data, dict):
            data = data.get(key, "MISSING")
        else:
            return "N/A"
    return data

def print_result(case_type: str, result: dict):
    """可视化打印验证结果"""
    print(f"\n🔧 测试类型: {case_type.upper()}")
    print("📝 验证结果:", "✅ 通过" if result["valid"] else "❌ 失败")

    if not result["valid"]:
        print("\n❌ 错误详情:")
        for error in result["errors"]:
            print(f"  🎯 字段路径: {error['field']}")
            print(f"  📌 错误信息: {error['message']}")
            print(f"  📥 输入内容: {error['input']}\n")

def main():
    """主测试流程"""
    test_cases = [
        ("valid", "合法配置"),
        ("invalid_env", "非法环境参数"),
        ("invalid_port", "非法端口号"),
        ("nested_error", "嵌套模型错误"),
        ("path_error", "路径类型错误"),
        ("random", "随机压力测试")
    ]

    for case_type, description in test_cases:
        # 生成测试配置
        config = generate_test_case(case_type)

        # 执行配置验证
        result = validate_config(config)

        # 打印可视化报告
        print(f"\n{'='*30}")
        print(f"🏁 开始测试: {description}")
        print_result(case_type, result)

if __name__ == "__main__":
    main()