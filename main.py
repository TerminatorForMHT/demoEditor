import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QApplication, QSplitter, QHBoxLayout, QMainWindow
from qfluentwidgets import FluentTitleBar
from qfluentwidgets.common.animation import BackgroundAnimationWidget
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow

from views.UserInterface import UserInterface


class MainWindow(BackgroundAnimationWidget, FramelessWindow):
    def __init__(self):
        super().__init__()
        self.ctrl_pressed = False
        self.setWindowTitle("Monaco Editor in Qt")
        self.resize(800, 600)

        self.Main_widget = UserInterface(self)

        self.hBoxLayout = QHBoxLayout(self)
        self.mainWidget = QWidget(self)
        self.widgetLayout = QVBoxLayout(self.mainWidget)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.mainWidget)
        self.widgetLayout.setContentsMargins(0, 30, 0, 0)
        self.widgetLayout.addWidget(self.mainWidget)
        self.setLayout(self.hBoxLayout)

        # 设置布局
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.addWidget(self.Main_widget)
        self.widgetLayout.addWidget(self.splitter)
        self.setTitleBar(FluentTitleBar(self))
        self.setWindowTitle('PythonPad++')


class MainWindow1(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ctrl_pressed = False
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.titleBar = FluentTitleBar(self)
        self.titleBar.raise_()
        self.setWindowTitle('PythonPad++')

        self.code_widget = UserInterface(self)

        # 设置布局
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.code_widget)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
