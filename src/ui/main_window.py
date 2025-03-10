from pathlib import Path
from typing import Any, Dict

from PySide6.QtWidgets import (
    QPushButton, QComboBox, QVBoxLayout, QWidget,
    QLabel, QLineEdit, QFileDialog, QMessageBox,
    QSpinBox, QStackedWidget, QCheckBox, QHBoxLayout,
    QSizePolicy, QFrame
)
from PySide6.QtGui import QAction, QDoubleValidator, QIcon, QFont
from PySide6.QtCore import Qt, Signal, QSize
import logging

from src.config import ViewParams
from src.factory.inputwidget_factory import InputWidgetFactory
from src.ui.interfaces import IMainWindow
from src.ui.styles import MAIN_STYLE

logger = logging.getLogger(__name__)


class StyledButton(QPushButton):
    """带图标的现代风格按钮"""

    def __init__(self, text, icon_path=None):
        super().__init__(text)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(20, 20))
        self.setMinimumSize(120, 40)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)


class MainWindow(IMainWindow):
    # 定义信号（用于向Presenter传递事件）
    folder_selected = Signal()
    opacity_changed = Signal(int)
    generate_triggered = Signal(int)
    menu_clicked = Signal(str)
    toggle_topmost = Signal(bool)

    def __init__(self):
        super().__init__()
        self._setup_window_properties()
        self._init_fonts()
        self.setStyleSheet(MAIN_STYLE)
        self.presenter: Any = None
        self.config: Dict[str, Any] = None
        # self._init_ui()

    def _setup_window_properties(self):
        """窗口初始化配置"""
        self.setWindowTitle("水印生成系统")
        self.setMinimumSize(600, 400)
        # self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)

    def _init_fonts(self):
        """字体初始化"""
        self.title_font = QFont("微软雅黑", 14, QFont.Bold)
        self.label_font = QFont("微软雅黑", 10)

    def show_error(self, message):
        QMessageBox.critical(self, "错误", message)

    def show_info(self, message):
        QMessageBox.information(self, "消息", message)

    def show_folder_dialog(self, default_path):
        return QFileDialog.getExistingDirectory(self, "选择文件夹", default_path)

    def set_folder_path(self, path):
        self.folder_input.setText(path)

    def get_folder_path(self):
        return self.folder_input.text()

    def initAfterInjection(self):
        self.toggle_topmost.emit(True)

    def set_window_topmost(self, is_topmost):
        flags = self.windowFlags()
        if is_topmost:
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

    def set_presenter(self, presenter):
        self.presenter = presenter

    def set_view_config(self, view_config: ViewParams):
        self.config = view_config
        self._init_ui()

    def _init_ui(self):

        self._create_menu_bar()
        self._create_main_content()

    def _create_param_inputs(self, params):
        container = QWidget()
        container.input_fields = {}
        layout = QVBoxLayout()

        def create_input_widget(config, default_value):
            """根据配置类型创建对应的输入组件"""
            input_type = config.get("input_type", "string")

            # 创建对应类型的输入组件
            if input_type == "QSpinBox":
                spinbox = QSpinBox()
                spinbox.setRange(config.get("min", 0), config.get("max", 100))
                spinbox.setValue(int(default_value))
                return spinbox, lambda: spinbox.value()

            elif input_type == "QComboBox":
                combo = QComboBox()
                combo.addItems([str(opt) for opt in config.get("options", [])])
                combo.setCurrentText(str(default_value))
                return combo, lambda: combo.currentText()

            elif input_type == "QCheckBox":
                check = QCheckBox()
                check.setChecked(self.config.get("default", True))
                return check, lambda: check.isChecked()

            # elif input_type == "color":
            #     color_btn = QPushButton()
            #     color_btn.setStyleSheet(f"background-color: {default_value}")
            #     color_btn.clicked.connect(lambda: self._pick_color(color_btn))
            #     return color_btn, lambda: color_btn.palette().button().color().name()
            else:  # 默认字符串类型
                line_edit = QLineEdit(str(default_value))
                if input_type == "float":
                    line_edit.setValidator(QDoubleValidator())
                return line_edit, lambda: line_edit.text()

        for param_key, param_config in params.items():
            widget, getter = InputWidgetFactory.create(param_config, param_config.get('default'))
            input_type = param_config.get("type", "string")

            # 创建界面元素
            q_label = QLabel(param_config.get('label', param_key))

            # 存储输入组件和取值函数
            container.input_fields[param_key] = {
                "widget": widget,
                "get_value": getter,
                "type": input_type
            }

            layout.addWidget(q_label)
            layout.addWidget(widget)

        container.setLayout(layout)
        return container

    def get_param_values(self, container):
        values = {}
        for param_key, field in container.input_fields.items():
            try:
                values[param_key] = field["get_value"]()
                # 可在此处添加类型转换和验证
            except Exception as e:
                print(f"参数 {param_key} 获取错误: {str(e)}")
        return values

    ### flags
    def get_watermark_params(self, wm_type):
        return {
            param: self.get_param_values(self.params_inputs[wm_type])[param]
            for param in self.config.watermark_types[wm_type]['params']
        }

    def _create_menu_bar(self):
        """现代风格菜单栏"""
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background: #F8F9FA;
                padding: 4px;
                border-bottom: 1px solid #DEE2E6;
            }
            QMenuBar::item {
                padding: 4px 8px;
            }
        """)
        # 文件菜单
        file_action = QAction("文件", self)
        file_action.triggered.connect(lambda: self.menu_clicked.emit("文件"))
        menu_bar.addAction(file_action)

        # # 窗口置顶
        # self.always_on_top_action = QAction("取消始终置顶", self)
        # self.always_on_top_action.setCheckable(True)
        # self.always_on_top_action.setChecked(True)
        # self.always_on_top_action.triggered.connect(
        #     lambda checked: self.toggle_topmost.emit(checked)
        # )
        # menu_bar.addAction(self.always_on_top_action)

    def _create_main_content(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # layout = QVBoxLayout()
        # layout.setContentsMargins(20, 10, 20, 20)
        # layout.setSpacing(15)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 10, 20, 20)
        main_layout.setSpacing(15)
        self._create_title_section(main_layout)
        self._create_watermark_selector(main_layout)
        self._create_folder_selection(main_layout)
        self._create_generate_button(main_layout)
        central_widget.setLayout(main_layout)

    def _create_title_section(self, layout):
        """标题区域"""
        title_label = QLabel("水印生成系统")
        title_label.setFont(self.title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

    def _create_watermark_selector(self, layout):
        """水印类型选择器"""
        selector_layout = QHBoxLayout()

        type_label = QLabel("水印类型:")
        type_label.setFont(self.label_font)
        selector_layout.addWidget(type_label)

        self.combo = QComboBox()
        self.combo.setFixedHeight(32)
        selector_layout.addWidget(self.combo, 3)

        layout.addLayout(selector_layout)

    def _create_watermark_selector(self, layout):
        self.combo = QComboBox()
        self.param_stack = QStackedWidget()  # 新增堆叠容器

        self.params_inputs = {
            wm_type: self._create_param_inputs(data['params'])
            for wm_type, data in self.config.watermark_types.items()
        }
        for wm_type, data in self.config.watermark_types.items():
            self.combo.addItem(data['display'], wm_type)
            # 为每种类型创建参数面板并添加到堆叠容器
            param_panel = self.params_inputs[wm_type]
            self.param_stack.addWidget(param_panel)

        # 连接选择变化信号
        self.combo.currentIndexChanged.connect(self.param_stack.setCurrentIndex)

        layout.addWidget(self.combo)
        layout.addWidget(self.param_stack)  # 替换原来的直接添加

    def _create_folder_selection(self, layout):
        # 文件夹选择
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("请选择文件夹")
        self.set_folder_path(str(Path('resources/input').resolve()))
        folder_button = QPushButton("选择文件夹")
        folder_button.clicked.connect(self._emit_folder_selected)
        layout.addWidget(self.folder_input)
        layout.addWidget(folder_button)

    def _create_generate_button(self, layout):
        # 生成按钮
        generate_btn = QPushButton("生成水印")
        generate_btn.clicked.connect(
            lambda: self.generate_triggered.emit(
                self.combo.currentIndex()
            )
        )
        layout.addWidget(generate_btn)

    def _emit_folder_selected(self):
        folder = self.folder_selected.emit()
        if folder:
            self.folder_input.text()

    def update_topmost_status(self, is_topmost):
        text = "取消始终置顶" if is_topmost else "始终置顶"
        self.always_on_top_action.setText(text)
        self.show()