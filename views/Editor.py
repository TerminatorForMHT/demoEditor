from PyQt6.QtCore import pyqtSignal
from monaco import MonacoWidget

from config.MAPS import MONACO_LANGUAGES
from config.config import ENCODE


class Editor(MonacoWidget):
    cursorPositionChanged = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.file_path = None

    def load_file(self, file_path) -> None:
        """
        加载文件
        :param file_path:文件路径
        """
        self.file_path = file_path
        file_suffix = file_path.split('.')[-1]
        print(file_suffix)
        language = MONACO_LANGUAGES.get(file_suffix, 'plaintext')
        print(language)
        self.setLanguage(language)
        with open(file_path, 'r', encoding=ENCODE) as f:
            self.setText(f.read())

    def save_file(self) -> None:
        """
        保存文件
        """
        with open(self.file_path, 'w', encoding=ENCODE) as f:
            f.write(self.text())

    def _handle_cursor_position(self, position):
        if position:
            self.cursorPositionChanged.emit(position[0], position[1])

    def get_cursor_position(self):
        script = """
        (function() {
            const position = editor.getPosition();
            return [position.lineNumber, position.column];
        })();
        """
        self.page().runJavaScript(script)

    def set_font_size(self, size: int):
        script = f"""
        (function() {{
            setEditorFontSize({size});
        }})();
        """

        self.page().runJavaScript(script)

    def set_font_family(self, font_family: str):
        script = f"""
        (function() {{
            setEditorFontFamily('{font_family}');
        }})();
        """

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
        启用 Ctrl+单击可获取光标位置。
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
        注册 PyQt 处理程序，供 JavaScript 调用。
        """

        class SignalHandler:
            def __init__(self, editor_instance):
                self.editor_instance = editor_instance

            def handleCtrlClick(self, line, column):
                self.editor_instance.ctrlClickPosition.emit(line, column)

        handler = SignalHandler(self)
        self.page().setWebChannel(handler)
