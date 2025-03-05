from pathlib import Path
from pydantic import ValidationError, BaseModel


class ProcessorParams(BaseModel):
    """参数基类（定义公共字段）"""
    opacity: float = 0.8
    output_dir: Path

def main():
    # 测试用例集合
    test_cases = [
        # 合法用例
        {
            "input": {"output_dir": Path("output")},
            "description": "使用默认透明度"
        },
        {
            "input": {"opacity": 0.5, "output_dir": Path("processed")},
            "description": "自定义透明度"
        },
        {
            "input": {"opacity": 1.0, "output_dir": Path("result") / "v1"},
            "description": "最大透明度"
        },

        # 非法用例
        {
            "input": {"opacity": -0.5, "output_dir": Path("error")},
            "description": "透明度低于最小值",
            "should_fail": True
        },
        {
            "input": {"opacity": "invalid", "output_dir": Path("error")},
            "description": "错误类型透明度",
            "should_fail": True
        },
        {
            "input": {"opacity": 0.5},
            "description": "缺少必要字段",
            "should_fail": True
        },
        {
            "input": {"opacity": 1.0, "output_dir": Path("result") / "v1"},
            "description": "我的问题"
        },
    ]

    # 执行测试
    for case in test_cases:
        print(f"\n=== 测试场景：{case['description']} ===")
        print(f"输入参数：{case['input']}")

        try:
            params = ProcessorParams(**case['input'])
            print("验证通过 ✅")
            print(f"生成参数对象：{params}")

            # 显示实际使用的值
            print(f"实际使用参数：")
            print(f"  - 透明度：{params.opacity} ({type(params.opacity)})")
            print(f"  - 输出目录：{params.output_dir} ({type(params.output_dir)})")

        except ValidationError as e:
            if not case.get('should_fail', False):
                print("意外验证失败 ❌")
            else:
                print("预期失败 ✅")

            print("错误详情：")
            for error in e.errors():
                print(f"  - 字段: {error['loc']}")
                print(f"    问题: {error['msg']}")
                print(f"    输入值: {case['input'].get(error['loc'], '未提供')}")

if __name__ == "__main__":
    main()