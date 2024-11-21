import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QDir


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monaco Editor in Qt")
        self.resize(800, 600)

        # 创建 WebEngineView
        web_view = QWebEngineView()
        # 加载离线 HTML 文件
        html_path = QDir.current().filePath("resources/index.html")
        web_view.setUrl(QUrl.fromLocalFile(html_path))

        # 设置布局
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(web_view)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
