from PyQt6.QtCore import pyqtSignal, QDir, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView


class Editor(QWebEngineView):
    cursorPositionChanged = pyqtSignal(int, int)  # 光标行列信号
    ctrlClickPosition = pyqtSignal(int, int)  # Ctrl+鼠标点击位置信号

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.html_path = QDir.current().filePath("resources/index.html")
        self.setUrl(QUrl.fromLocalFile(self.html_path))

    def set_editor_content(self, content: str):
        script = f"setEditorContent(`{content.replace('`', '\\`')}`);"
        self.page().runJavaScript(script)
        self.enable_ctrl_click()

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

    def add_underline_marker(self, start_line: int, start_col: int, end_line: int, end_col: int, color: str = "red"):
        class_name = "underline-red" if color == "red" else "underline-yellow"
        script = f"""
        (function() {{
            const decoration = {{
                range: new monaco.Range({start_line}, {start_col}, {end_line}, {end_col}),
                options: {{
                    inlineClassName: '{class_name}'
                }}
            }};
            editor.deltaDecorations([], [decoration]);
        }})();
        """
        self.page().runJavaScript(script)

    def jump_to_position(self, line: int, column: int):
        script = f"""
        (function() {{
            editor.revealPosition({{ lineNumber: {line}, column: {column} }});
            editor.setPosition({{ lineNumber: {line}, column: {column} }});
            editor.focus();
        }})();
        """
        self.page().runJavaScript(script)

    def enable_ctrl_click(self):
        """
        Enables Ctrl+Click to get the cursor position.
        """
        script = """
        (function() {
            editor.onMouseDown(function(e) {
                if (e.event.ctrlKey && e.target.position) {
                    const position = e.target.position;
                    window.pyqtSignalHandler.handleCtrlClick(position.lineNumber, position.column);
                }
            });
        })();
        """
        self.page().runJavaScript(script)

    def _register_pyqt_handler(self):
        """
        Registers a PyQt handler for JavaScript to call.
        """

        class SignalHandler:
            def __init__(self, editor_instance):
                self.editor_instance = editor_instance

            def handleCtrlClick(self, line, column):
                self.editor_instance.ctrlClickPosition.emit(line, column)

        handler = SignalHandler(self)
        self.page().setWebChannel(handler)
