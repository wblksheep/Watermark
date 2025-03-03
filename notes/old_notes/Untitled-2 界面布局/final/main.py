import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QPushButton, QComboBox, QVBoxLayout, QWidget, QLabel, QLineEdit, QFileDialog
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from basic_2 import generate_watermark
import glob
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("界面示例")
        self.setGeometry(100, 100, 400, 300)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建主界面内容
        self.create_main_content()

    def create_menu_bar(self):
        # 创建菜单栏
        menu_bar = self.menuBar()

        # 创建文件菜单
        file_menu = menu_bar.addMenu("文件")
        new_action = QAction("新建", self)
        file_menu.addAction(new_action)
        open_action = QAction("打开", self)
        file_menu.addAction(open_action)
        save_action = QAction("保存", self)
        file_menu.addAction(save_action)

        # 创建编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        cut_action = QAction("剪切", self)
        edit_menu.addAction(cut_action)
        copy_action = QAction("复制", self)
        edit_menu.addAction(copy_action)
        paste_action = QAction("粘贴", self)
        edit_menu.addAction(paste_action)
        #创建“窗口”菜单
        window_menu = menu_bar.addMenu("窗口")
        
        self.always_on_top_action = QAction("取消始终置顶", self)
        self.always_on_top_action.setCheckable(True)
        self.always_on_top_action.setChecked(True)
        self.always_on_top_action.triggered.connect(self.toggle_always_on_top)
        window_menu.addAction(self.always_on_top_action)
        self.toggle_always_on_top()
    
    def toggle_always_on_top(self):
        if self.always_on_top_action.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.always_on_top_action.setText("取消始终置顶")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.always_on_top_action.setText("始终置顶")
        self.show()

    def create_main_content(self):
        # 创建主窗口的中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建布局
        layout = QVBoxLayout()

        # 创建标签
        label = QLabel("界面示例")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(label)

        # 创建下拉菜单
        self.combo_box = QComboBox()
        self.combo_box.addItems(["选项 1", "选项 2", "选项 3"])
        self.combo_box.setStyleSheet("""
            QComboBox {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right top;
                width: 20px;
                border-left: 1px solid #ccc;
            }
            QComboBox::down-arrow {
                image: url(none);
            }
        """)
        layout.addWidget(self.combo_box)

        # 创建文件夹选择输入框和按钮
        folder_layout = QVBoxLayout()

        # 输入框
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("请选择文件夹")
        self.folder_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
        """)
        folder_layout.addWidget(self.folder_input)

        # 按钮
        folder_button = QPushButton("选择文件夹")
        folder_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 14px;
                background-color: #008CBA;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #007B9E;
            }
        """)
        folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(folder_button)

        layout.addLayout(folder_layout)
        # 不透明度输入框
        self.opacity_input = QLineEdit()
        self.opacity_input.setPlaceholderText("请输入不透明度，默认50%")
        self.opacity_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
        """)
        layout.addWidget(self.opacity_input)
        # 创建按钮
        button = QPushButton("点击我")
        button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(button)
        button.clicked.connect(self.button_click_event)
        # 设置布局
        central_widget.setLayout(layout)
    
    def button_click_event(self):
        def switch(case):
            cases={
                0: "watermark_mask_300",
                1: "选项 2",
                2: "选项 3"
            }
            return cases.get(case, "默认选项")
        current_index = self.combo_box.currentIndex()
        print(switch(current_index))
        if self.opacity_input.text()!="":
            final_opacity = int(self.opacity_input.text())
            for file_path in glob.glob(os.path.join(self.folder_input.text(), "*")):
                # 检查文件是否是普通文件（而不是文件夹）
                if os.path.isfile(file_path):
                    basename = os.path.basename(file_path)
                    generate_watermark(basename, switch(current_index), final_opacity=final_opacity)
                    print(basename)
        else:
            for file_path in glob.glob(os.path.join(self.folder_input.text(), "*")):
                # 检查文件是否是普通文件（而不是文件夹）
                if os.path.isfile(file_path):
                    basename = os.path.basename(file_path)
                    generate_watermark(basename, switch(current_index), final_opacity=50)
                    print(basename)


        
    

    
    def select_folder(self):
        # 打开文件夹选择对话框
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            self.folder_input.setText(folder_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())