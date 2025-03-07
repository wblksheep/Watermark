from pathlib import Path
from typing import Any, Dict, Callable

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

class InputWidgetFactory:
    """参数输入组件工厂类"""
    @staticmethod
    def create(config: Dict, default_value: Any) -> tuple[QWidget, Callable]:
        input_type = config.get("input_type", "string")

        widget_creators = {
            "QSpinBox": InputWidgetFactory._create_spinbox,
            "QComboBox": InputWidgetFactory._create_combobox,
            "QCheckBox": InputWidgetFactory._create_checkbox,
            "float": InputWidgetFactory._create_float_input,
        }
        return widget_creators.get(input_type, InputWidgetFactory._create_default_input)(config, default_value)

    @staticmethod
    def _create_spinbox(config, default):
        widget = QSpinBox()
        widget.setRange(config.get("min", 0), config.get("max", 100))
        widget.setValue(int(default))
        return widget, widget.value

    @staticmethod
    def _create_combobox(config, default):
        widget = QComboBox()
        widget.addItems(map(str, config.get("options", [])))
        widget.setCurrentText(str(default))
        return widget, lambda: widget.currentText()

    @staticmethod
    def _create_checkbox(config, default):
        widget = QCheckBox()
        widget.setChecked(bool(default))
        return widget, widget.isChecked

    @staticmethod
    def _create_float_input(config, default):
        widget = QLineEdit(str(default))
        widget.setValidator(QDoubleValidator())
        return widget, lambda: float(widget.text())

    @staticmethod
    def _create_default_input(config, default):
        widget = QLineEdit(str(default))
        return widget, lambda: widget.text()

class MainWindow(IMainWindow):
    # 定义信号（用于向Presenter传递事件）
    folder_selected = Signal()
    opacity_changed = Signal(int)
    generate_triggered = Signal(int)
    menu_clicked = Signal(str)
    toggle_topmost = Signal(bool)

    def __init__(self):
        super().__init__()
        self._init_ui_properties()
        self.presenter: Any = None
        self.config: ViewParams = None
        self.params_inputs: Dict[str, QWidget] = {}

    def _init_ui_properties(self):
        """界面属性初始化"""
        self.setWindowTitle("水印生成系统")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(MAIN_STYLE)
        self._init_fonts()

    def _init_fonts(self):
        """字体初始化"""
        self.title_font = QFont("微软雅黑", 16, QFont.Bold)
        self.label_font = QFont("微软雅黑", 10)
        self.button_font = QFont("微软雅黑", 10, QFont.Medium)

    def initAfterInjection(self):
        self.toggle_topmost.emit(True)

    def set_presenter(self, presenter):
        self.presenter = presenter

    def set_view_config(self, view_config: ViewParams):
        self.config = view_config
        self._init_ui()

    def _init_ui(self):

        self._create_menu_bar()
        self._create_main_content()

    def _create_main_content(self):
        """主内容区域"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 25)
        main_layout.setSpacing(20)

        self._create_header_section(main_layout)
        self._create_config_section(main_layout)
        self._create_action_section(main_layout)

        central_widget.setLayout(main_layout)

    def _create_header_section(self, layout):
        """头部区域"""
        header = QWidget()
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 10)

        title = QLabel("AI 智能水印生成系统")
        title.setFont(self.title_font)
        title.setAlignment(Qt.AlignCenter)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #E0E0E0;")

        vbox.addWidget(title)
        vbox.addWidget(separator)
        header.setLayout(vbox)
        layout.addWidget(header)

    def _create_config_section(self, layout):
        """配置区域"""
        config_container = QWidget()
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(15, 15, 15, 20)
        config_layout.setSpacing(15)

        self._create_watermark_selector(config_layout)
        self._create_folder_picker(config_layout)
        self._create_parameter_stack(config_layout)

        config_container.setLayout(config_layout)
        config_container.setStyleSheet("""
            background: #FFFFFF;
            border-radius: 8px;
            border: 1px solid #E0E0E0;
        """)
        layout.addWidget(config_container)

    def _create_watermark_selector(self, layout):
        """水印类型选择器"""
        selector_container = QWidget()
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        label = QLabel("水印模式:")
        label.setFont(self.label_font)

        self.type_combo = QComboBox()
        self.type_combo.setFixedHeight(36)
        self.type_combo.setFont(self.label_font)

        hbox.addWidget(label)
        hbox.addWidget(self.type_combo, 1)
        hbox.addSpacing(10)

        selector_container.setLayout(hbox)
        layout.addWidget(selector_container)

    def _create_folder_picker(self, layout):
        """现代风格路径选择器"""
        picker_container = QWidget()
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("点击右侧按钮选择输入目录...")
        self.path_input.setReadOnly(True)
        self.path_input.setFixedHeight(36)

        pick_btn = QPushButton()
        pick_btn.setIcon(QIcon(":/icons/folder.svg"))
        pick_btn.setFixedSize(36, 36)
        pick_btn.clicked.connect(self._emit_folder_selected)

        hbox.addWidget(self.path_input)
        hbox.addWidget(pick_btn)
        picker_container.setLayout(hbox)
        layout.addWidget(picker_container)

    def _create_parameter_stack(self, layout):
        """参数堆栈优化"""
        self.param_stack = QStackedWidget()
        self.param_stack.setStyleSheet("""
            QStackedWidget {
                background: #F8F9FA;
                border-radius: 6px;
                padding: 15px;
            }
        """)

        # 初始化参数面板
        for wm_type, config in self.config.watermark_types.items():
            panel = self._create_parameter_panel(config['params'])
            self.param_stack.addWidget(panel)
            self.params_inputs[wm_type] = panel

        layout.addWidget(self.param_stack)
        self.type_combo.currentIndexChanged.connect(self.param_stack.setCurrentIndex)

    def _create_parameter_panel(self, params: Dict) -> QWidget:
        """创建参数面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        for param_name, config in params.items():
            widget, getter = InputWidgetFactory.create(config, config.get('default'))

            row = QHBoxLayout()
            label = QLabel(config.get('label', param_name))
            label.setFont(self.label_font)

            row.addWidget(label, 1)
            row.addWidget(widget, 2)
            layout.addLayout(row)

            # 存储组件引用
            setattr(panel, f"{param_name}_widget", widget)
            setattr(panel, f"get_{param_name}", getter)

        panel.setLayout(layout)
        return panel

    ### flags

    def _create_action_section(self, layout):
        # 生成按钮
        generate_btn = QPushButton("生成水印")
        generate_btn.clicked.connect(
            lambda: self.generate_triggered.emit(
                self.type_combo.currentIndex()
            )
        )
        layout.addWidget(generate_btn)

    def get_watermark_params(self, wm_type: str) -> Dict:
        """获取参数优化"""
        panel = self.params_inputs.get(wm_type)
        if not panel:
            return {}

        return {
            param: getattr(panel, f"get_{param}")()
            for param in self.config.watermark_types[wm_type]['params']
        }

    def get_param_values(self, container):
        values = {}
        for param_key, field in container.input_fields.items():
            try:
                values[param_key] = field["get_value"]()
                # 可在此处添加类型转换和验证
            except Exception as e:
                print(f"参数 {param_key} 获取错误: {str(e)}")
        return values

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

        # 窗口置顶
        self.always_on_top_action = QAction("取消始终置顶", self)
        self.always_on_top_action.setCheckable(True)
        self.always_on_top_action.setChecked(True)
        self.always_on_top_action.triggered.connect(
            lambda checked: self.toggle_topmost.emit(checked)
        )
        menu_bar.addAction(self.always_on_top_action)

    def _emit_folder_selected(self):
        folder = self.folder_selected.emit()
        if folder:
            self.folder_input.text()


    def update_topmost_status(self, is_topmost):
        text = "取消始终置顶" if is_topmost else "始终置顶"
        self.always_on_top_action.setText(text)
        self.show()

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

    def set_window_topmost(self, is_topmost):
        flags = self.windowFlags()
        if is_topmost:
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)


