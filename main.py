import sys

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QApplication

from view.CodeWidget import CodeWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("代码编辑器")
        self.setGeometry(100, 100, 800, 600)  # 窗口大小和位置

        # 创建主窗口的中央部件
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # 创建布局
        self.layout = QVBoxLayout(self.central_widget)
        self.central_widget.setLayout(self.layout)

        # 创建按钮
        self.open_file_button = QPushButton("打开文件", self)
        self.open_file_button.clicked.connect(self.open_file)
        self.layout.addWidget(self.open_file_button)

        # 创建CodeWidget实例
        self.code_widget = CodeWidget(self)
        self.layout.addWidget(self.code_widget)

    def open_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Python files (*.py)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            print(f"Selected file: {file_path}")
            self.code_widget.load_file(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
