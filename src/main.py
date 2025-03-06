import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.config_loader.config_loader import ConfigLoader
from src.container import Container
from config import setup_logging, AppConfig


def main():
    app = QApplication(sys.argv)
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # 加载配置
        config = ConfigLoader.load_config(
            Path('config.yaml'),
            AppConfig
        )
        container = Container()
        presenter = container.presenter(config=config)
        view = container.view()
        view.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.exception(e)
        # raise Exception(e)


if __name__ == "__main__":
    main()