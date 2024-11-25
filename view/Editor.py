from PyQt6.QtCore import pyqtSignal, QDir, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView


class Editor(QWebEngineView):
    cursorPositionChanged = pyqtSignal(int, int)  # 光标行列信号

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.html_path = QDir.current().filePath("resources/index.html")
        self.setUrl(QUrl.fromLocalFile(self.html_path))

    def set_editor_content(self, content: str):
        script = f"setEditorContent(`{content.replace('`', '\\`')}`);"
        self.page().runJavaScript(script)

    def get_cursor_position(self):
        script = """
        (function() {
            const position = editor.getPosition();
            return [position.lineNumber, position.column];
        })();
        """
        self.page().runJavaScript(script, self._handle_cursor_position)

    def _handle_cursor_position(self, position):
        if position:
            self.cursorPositionChanged.emit(position[0], position[1])

    def set_font_size(self, size: int):
        script = f"setEditorFontSize({size});"
        self.page().runJavaScript(script)

    def set_theme(self, theme: str):
        script = f"setEditorTheme('{theme}');"
        self.page().runJavaScript(script)

    def set_font_family(self, font_family: str):
        script = f"setEditorFontFamily('{font_family}');"
        self.page().runJavaScript(script)
