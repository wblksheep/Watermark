import logging
import sys
from PySide6.QtWidgets import QApplication
from container import Container
from config import setup_logging

def main():
    app = QApplication(sys.argv)
    setup_logging()
    logger = logging.getLogger(__name__)
    try:
        container = Container()
        container.config.from_dict({
            "default_opacity": 50,
        })
        presenter = container.presenter()
        view = container.view()
        view.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.exception(e)
        # raise Exception(e)


if __name__ == "__main__":
    main()