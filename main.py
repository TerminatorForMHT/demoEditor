import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QFileDialog, QSpinBox, QComboBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QDir, pyqtSlot, pyqtSignal, QObject


class EditorBridge(QObject):
    cursorPositionChanged = pyqtSignal(int, int)  # 光标行列信号

    def __init__(self, web_view):
        super().__init__()
        self.web_view = web_view

    def set_editor_content(self, content: str):
        script = f"setEditorContent(`{content.replace('`', '\\`')}`);"
        self.web_view.page().runJavaScript(script)

    def get_cursor_position(self):
        script = """
        (function() {
            const position = editor.getPosition();
            return [position.lineNumber, position.column];
        })();
        """
        self.web_view.page().runJavaScript(script, self._handle_cursor_position)

    def _handle_cursor_position(self, position):
        if position:
            self.cursorPositionChanged.emit(position[0], position[1])

    def set_font_size(self, size: int):
        script = f"setEditorFontSize({size});"
        self.web_view.page().runJavaScript(script)

    def set_theme(self, theme: str):
        script = f"setEditorTheme('{theme}');"
        self.web_view.page().runJavaScript(script)

    def set_font_family(self, font_family: str):
        script = f"setEditorFontFamily('{font_family}');"
        self.web_view.page().runJavaScript(script)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monaco Editor in Qt")
        self.resize(1000, 700)

        # 编辑器 WebEngineView
        self.web_view = QWebEngineView()
        html_path = QDir.current().filePath("resources/index.html")
        self.web_view.setUrl(QUrl.fromLocalFile(html_path))

        # 编辑器交互桥
        self.bridge = EditorBridge(self.web_view)

        # 主界面布局
        container = QWidget()
        layout = QVBoxLayout(container)

        # 工具栏布局
        toolbar = QHBoxLayout()

        # 打开文件按钮
        open_file_btn = QPushButton("打开文件")
        open_file_btn.clicked.connect(self.open_file)

        # 字体大小设置
        font_label = QLabel("字体大小:")
        font_spinbox = QSpinBox()
        font_spinbox.setRange(8, 40)
        font_spinbox.setValue(14)
        font_spinbox.valueChanged.connect(self.bridge.set_font_size)

        # 字体类别设置
        font_family_label = QLabel("字体:")
        font_family_combo = QComboBox()
        font_family_combo.addItems(["Consolas", "Courier New", "Monaco", "Fira Code"])
        font_family_combo.currentTextChanged.connect(self.bridge.set_font_family)

        # 深色/浅色主题切换按钮
        theme_btn = QPushButton("切换主题")
        self.is_dark_theme = True
        theme_btn.clicked.connect(self.toggle_theme)

        # 光标位置按钮
        cursor_btn = QPushButton("获取光标位置")
        cursor_btn.clicked.connect(self.get_cursor_position)

        # 添加到工具栏
        toolbar.addWidget(open_file_btn)
        toolbar.addWidget(font_label)
        toolbar.addWidget(font_spinbox)
        toolbar.addWidget(font_family_label)
        toolbar.addWidget(font_family_combo)
        toolbar.addWidget(theme_btn)
        toolbar.addWidget(cursor_btn)

        # 光标位置显示

        self.bridge.cursorPositionChanged.connect(self.print_cursor_label)

        # 布局设置
        layout.addLayout(toolbar)
        layout.addWidget(self.web_view)
        self.setCentralWidget(container)

    def resizeEvent(self, event):
        self.web_view.resize(self.size())
        super().resizeEvent(event)

    @pyqtSlot()
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "打开文件", "", "所有文件 (*.*)")
        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                content = file.read()
            self.bridge.set_editor_content(content)

    @pyqtSlot()
    def get_cursor_position(self):
        self.bridge.get_cursor_position()

    @pyqtSlot(int, int)
    def print_cursor_label(self, line, column):
        print(f"光标位置: 行 {line}, 列 {column}")

    @pyqtSlot()
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        theme = "vs-dark" if self.is_dark_theme else "vs"
        self.bridge.set_theme(theme)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.showMaximized()
    window.show()
    sys.exit(app.exec())
