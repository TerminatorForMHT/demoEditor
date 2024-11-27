import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog

from views.Editor import Editor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monaco Editor in Qt")
        self.resize(800, 600)

        self.open_file_button = QPushButton("打开文件")
        self.open_file_button.clicked.connect(self.open_file)

        self.get_position_button = QPushButton("获取坐标")
        self.get_position_button.clicked.connect(self.get_cursor_position)

        self.monaco_widget = Editor(self)

        # 设置布局
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.open_file_button)
        layout.addWidget(self.get_position_button)
        layout.addWidget(self.monaco_widget)
        self.setCentralWidget(container)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py)")
        if file_path:
            self.monaco_widget.load_file(file_path)

    def get_cursor_position(self):
        cursor_position = self.monaco_widget.get_cursor_position()
        if cursor_position:
            print(f"Cursor Position: Line {cursor_position['lineNumber']}, Column {cursor_position['column']}")
        else:
            print("Failed to get cursor position.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
