from typing import Dict, Callable, Any

from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QWidget, QSpinBox, QComboBox, QCheckBox, QLineEdit


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