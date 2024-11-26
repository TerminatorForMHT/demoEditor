import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog

from views.Editor import Editor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monaco Editor in Qt")
        self.resize(800, 600)

        self.open_file_button = QPushButton("Open File")
        self.open_file_button.clicked.connect(self.open_file)

        self.monaco_widget = Editor()

        # 设置布局
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.open_file_button)
        layout.addWidget(self.monaco_widget)
        self.setCentralWidget(container)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py)")
        if file_path:
            self.monaco_widget.load_file(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
