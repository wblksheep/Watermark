import logging
import sys
import os
from pathlib import Path

# ---------------------------- 日志初始化 ----------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------------------------- 初始路径信息 ----------------------------
logger.info("=============== 应用启动 ===============")
logger.debug(f"[启动阶段] 当前工作目录: {os.getcwd()}")
logger.debug(f"[启动阶段] 系统路径 sys.path:\n{'\n'.join(sys.path)}")
logger.debug(f"[启动阶段] Python解释器路径: {sys.executable}")
logger.debug(f"[启动阶段] 脚本入口文件: {__file__}")

# ---------------------------- 关键库导入追踪 ----------------------------
try:
    logger.debug("[模块导入] 尝试导入 PySide6.QtWidgets...")
    from PySide6.QtWidgets import QApplication
    logger.debug(f"[模块导入] PySide6 成功导入，模块路径: {os.path.dirname(QApplication.__name__)}")
except ImportError as e:
    logger.error("[模块导入] PySide6 导入失败！")
    logger.exception(e)
    sys.exit(1)

try:
    logger.debug("[模块导入] 尝试导入 container 模块...")
    from container import Container
    logger.debug(f"[模块导入] container 模块路径: {Container.__module__}")
except ImportError as e:
    logger.error("[模块导入] container 模块导入失败，可能路径配置错误！")
    logger.exception(e)
    sys.exit(1)

try:
    logger.debug("[模块导入] 尝试导入 config 模块...")
    from config import setup_logging, AppConfig
    logger.debug(f"[模块导入] config 模块路径: {os.path.abspath(__import__('config').__file__)}")
except ImportError as e:
    logger.error("[模块导入] config 模块导入失败，检查文件是否存在！")
    logger.exception(e)
    sys.exit(1)

try:
    logger.debug("[模块导入] 尝试导入 src.config_loader...")
    from src.config_loader import ConfigLoader
    logger.debug(f"[模块导入] ConfigLoader 路径: {ConfigLoader.__module__}")
except ImportError as e:
    logger.error("[模块导入] src.config_loader 导入失败，检查 src 目录结构！")
    logger.exception(e)
    sys.exit(1)

# ---------------------------- 函数定义 ----------------------------
def get_base_path():
    """获取资源基准路径（添加详细日志）"""
    logger.debug("[路径解析] 开始计算基础路径...")
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
        logger.debug(f"[路径解析] 处于冻结环境，基础路径: {base_path}")
    else:
        base_path = Path(__file__).parent
        logger.debug(f"[路径解析] 处于开发环境，基础路径: {base_path}")

    logger.debug(f"[路径解析] 最终 base_path 是否存在: {base_path.exists()}")
    logger.debug(f"[路径解析] base_path 内容列表:\n{', '.join(os.listdir(base_path))}")
    return base_path

def main():
    logger.info("=============== 进入 main 函数 ===============")
    logger.debug(f"[main函数] 当前工作目录: {os.getcwd()}")
    logger.debug(f"[main函数] 更新后的 sys.path:\n{'\n'.join(sys.path)}")

    try:
        app = QApplication(sys.argv)
        logger.debug("QApplication 实例已创建")

        # ---------------------------- 配置加载 ----------------------------
        base_path = get_base_path()
        config_path = base_path / 'config.yaml'
        logger.debug(f"[配置加载] 尝试加载配置文件: {config_path.absolute()}")
        logger.debug(f"[配置加载] 配置文件是否存在: {config_path.exists()}")
        if not config_path.exists():
            logger.error(f"[配置加载] 配置文件不存在！搜索路径: {config_path.resolve()}")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        logger.debug("[配置加载] 开始加载配置文件...")
        config = ConfigLoader.load_config(config_path, AppConfig)
        logger.info("配置文件加载成功")
        logger.debug(f"[配置内容] 当前配置: {config}")

        # ---------------------------- 依赖注入 ----------------------------
        logger.debug("[依赖注入] 初始化容器...")
        container = Container()
        logger.debug(f"[依赖注入] 容器对象类型: {type(container)}")

        logger.debug("[依赖注入] 创建 Presenter...")
        presenter = container.presenter(config=config)
        logger.debug(f"[依赖注入] Presenter 类型: {type(presenter)}")

        logger.debug("[依赖注入] 创建 View...")
        view = container.view()
        logger.debug(f"[依赖注入] View 类型: {type(view)}")

        logger.debug("[界面显示] 准备显示主窗口...")
        view.show()
        logger.info("主窗口已显示")

        sys.exit(app.exec())
    except Exception as e:
        logger.error("[严重错误] 主流程异常终止！")
        logger.exception(e)
        sys.exit(1)

if __name__ == "__main__":
    main()