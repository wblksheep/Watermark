from PySide6.QtCore import QObject, Qt
from typing import Dict, Any, Callable
from functools import lru_cache
import logging

from src.config import AppConfig

logger = logging.getLogger(__name__)


class MainPresenter(QObject):
    _SIGNAL_BINDINGS = [
        ('generate_triggered', 'handle_selection'),
        ('folder_selected', 'handle_folder_selection'),
        # ('toggle_topmost', 'toggle_window_topmost'),
        ('menu_clicked', 'on_menu_click')
    ]
    _handler_map: Dict[str, Callable]

    def __init__(self, view, model, config: AppConfig):
        super().__init__()
        self._config = config
        self.view = view
        self.model = model
        self._handler_map = {}
        self._connect_signals()
        self.view.set_presenter(self)
        self.view.set_view_config(self._config.view_params)
        self.view.initAfterInjection()
        self.model.dependency_inject_after_init(self._config.model_params)
        # 延迟加载大配置项
        self._watermark_config = None
        self._bind_handlers()

    @property
    def watermark_config(self):
        if not self._watermark_config:
            self._watermark_config = self.model.load_watermark_config()
        return self._watermark_config

    def _bind_handlers(self):
        # 动态绑定配置中的处理器
        for wm_type in self.model.config.watermark_types:
            self._register_handler(wm_type)

    def _register_handler(self, wm_type: str):
        handler = self._create_handler(wm_type)
        setattr(self, f"handle_{wm_type}", handler)
        # 注册到路由表
        self._handler_map[wm_type] = handler

    def _create_handler(self, wm_type):
        def handler():
            try:
                input_folder = self.view.get_input_folder_path()
                output_folder = self.view.get_output_folder_path()
                params = self._collect_params(wm_type)
                result = self.model.get_handler(wm_type)(input_folder, output_folder, **params)

                #更新视图
                self.view.show_info(f"已为{len(result)}个图片添加水印")
            except Exception as e:
                logger.exception(e)
                self.view.show_error(f"{wm_type} 处理失败: {str(e)}")
        return handler

    def _collect_params(self, wm_type) -> Dict[str, Any]:
        # 合并配置默认值与用户输入
        default_params = self.model.config.watermark_types[wm_type]['params']
        user_params = self.view.get_watermark_params(wm_type)
        return {**default_params, **user_params}

    def _connect_signals(self):
        # 连接视图信号
        for signal_name, handler_name in self._SIGNAL_BINDINGS:
            getattr(self.view, signal_name).connect(getattr(self, handler_name))

    def on_menu_click(self, item):
        print(f"点击了菜单项: {item}")

    def handle_folder_selection(self):
        selected_path = self.view.show_folder_dialog("resources/input")
        if selected_path:
            # 通过接口更新视图
            self.view.set_input_folder_path(selected_path)
        selected_path = self.view.show_folder_dialog("output")
        if selected_path:
            # 通过接口更新视图
            self.view.set_output_folder_path(selected_path)

    # def toggle_window_topmost(self, is_topmost):
    #     # 将具体 flag 操作移至 View
    #     self.view.set_window_topmost(is_topmost)
    #     self.view.update_topmost_status(is_topmost)


    def handle_selection(self, index):
        handler_name = [wm_type for wm_type, _ in self.model.config.watermark_types.items()][index]
        handler = getattr(self, f"handle_{handler_name}", self._default_handler)
        handler()

    def _default_handler(self):
        print("未知选项，使用默认处理")