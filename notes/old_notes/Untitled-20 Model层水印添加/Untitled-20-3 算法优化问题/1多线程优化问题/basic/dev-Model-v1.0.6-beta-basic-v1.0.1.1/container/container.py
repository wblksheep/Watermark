from ui.main_window import MainWindow
from presenter.main_presenter import MainPresenter
from models.watermark_model import WatermarkModel
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    """依赖注入容器"""
    config = providers.Configuration()

    model = providers.Singleton(
        WatermarkModel
    )

    view = providers.Singleton(
        MainWindow
    )

    presenter = providers.Singleton(
        MainPresenter,
        view=view,
        model=model
    )