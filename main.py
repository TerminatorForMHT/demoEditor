import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from views.CodeWidget import CodeWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ctrl_pressed = False
        self.setWindowTitle("Monaco Editor in Qt")
        self.resize(800, 600)

        self.open_file_button = QPushButton("打开文件")
        self.open_file_button.clicked.connect(self.open_file)

        self.get_position_button = QPushButton("获取坐标")
        self.get_position_button.clicked.connect(self.get_cursor_position)

        self.code_widget = CodeWidget(self)

        # 设置布局
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.open_file_button)
        layout.addWidget(self.get_position_button)
        layout.addWidget(self.code_widget)
        self.setCentralWidget(container)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py)")
        if file_path:
            self.code_widget.load_file(file_path)

    def get_cursor_position(self):
        cursor_position = self.code_widget.stacked_widget.currentWidget().get_cursor_position()
        if cursor_position:
            print(f"Cursor Position: Line {cursor_position['lineNumber']}, Column {cursor_position['column']}")
        else:
            print("Failed to get cursor position.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
