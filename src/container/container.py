
from src.presenter.main_presenter import MainPresenter
from src.models.watermark_model import WatermarkModel
from dependency_injector import containers, providers

from src.ui.main_window import MainWindow


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