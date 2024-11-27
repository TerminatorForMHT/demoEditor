import autopep8
from PyQt6.QtCore import pyqtSignal, QEventLoop, Qt
from monaco import MonacoWidget

from config.MAPS import MONACO_LANGUAGES
from config.config import ENCODE
from util.jediLib import JdeiLib


class Editor(MonacoWidget):
    """
    自定义编辑器类，继承自 MonacoWidget
    """
    ctrl_left_click_signal = pyqtSignal(dict)
    code_execut_signal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.file_path = None

    def load_file(self, file_path: str) -> None:
        """
        加载文件内容到编辑器，并根据文件后缀设置语言。
        :param file_path: 文件路径
        """
        self.file_path = file_path
        file_suffix = file_path.rsplit('.', 1)[-1].lower()  # 防止后缀大小写差异
        language = MONACO_LANGUAGES.get(file_suffix, 'plaintext')
        self.setLanguage(language)

        try:
            with open(file_path, 'r', encoding=ENCODE) as file:
                self.setText(file.read())
                self._enable_ctrl_click()
        except Exception as error:
            self.setText(f"无法加载文件: {error}")

    def save_file(self) -> None:
        """
        保存当前编辑器内容到文件。
        """
        if not self.file_path:
            raise ValueError("未指定文件路径，无法保存。")

        try:
            with open(self.file_path, 'w', encoding=ENCODE) as file:
                file.write(self.text())
        except Exception as error:
            print(f"保存文件失败: {error}")

    def get_cursor_position(self):
        """
        获取光标位置并返回坐标 (行号, 列号)。
        """
        js_code = """
        (function() {
            if (editor) {
                const position = editor.getPosition();
                return {
                    lineNumber: position.lineNumber,
                    column: position.column
                };
            }
            return null;
        })();
        """

        # 创建事件循环等待 JavaScript 的异步返回值
        loop = QEventLoop()
        result = {"position": None}  # 使用字典存储返回值

        def handle_cursor_position(position):
            result["position"] = position  # 存储光标位置
            loop.quit()  # 结束事件循环

        # 运行 JavaScript 并设置回调
        self.page().runJavaScript(js_code, handle_cursor_position)
        loop.exec()  # 阻塞直到 JavaScript 执行完毕

        # 返回结果或 None
        return result["position"]

    def get_selected_text(self) -> str:
        """
        获取当前选中的文本。
        :return: 选中的文本
        """
        script = ""

    def set_font_size(self, size: int) -> None:
        """
        设置编辑器字体大小。
        :param size: 字体大小
        """
        self._execute_script(f"setEditorFontSize({size});")

    def set_font_family(self, font_family: str) -> None:
        """
        设置编辑器字体。
        :param font_family: 字体名称
        """
        self._execute_script(f"setEditorFontFamily('{font_family}');")

    def add_underline_marker(self, start_line: int, start_col: int, end_line: int, end_col: int,
                             color: str = "red") -> None:
        """
        在指定范围添加下划线标记。
        :param start_line: 起始行
        :param start_col: 起始列
        :param end_line: 结束行
        :param end_col: 结束列
        :param color: 标记颜色，默认为红色
        """
        class_name = "underline-red" if color == "red" else "underline-yellow"
        script = f"""
        (function() {{
            const decoration = {{
                range: new monaco.Range({start_line}, {start_col}, {end_line}, {end_col}),
                options: {{ inlineClassName: '{class_name}' }}
            }};
            editor.deltaDecorations([], [decoration]);
        }})();
        """
        self._execute_script(script)

    def jump_to_position(self, line: int, column: int) -> None:
        """
        跳转到指定的行列。
        :param line: 行号
        :param column: 列号
        """
        script = f"""
        (function() {{
            editor.revealPosition({{ lineNumber: {line}, column: {column} }});
            editor.setPosition({{ lineNumber: {line}, column: {column} }});
            editor.focus();
        }})();
        """
        self._execute_script(script)

    def _enable_ctrl_click(self) -> None:
        """
        启用 Ctrl+单击以捕获光标位置。
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
        self._execute_script(script)

    def _execute_script(self, script: str) -> None:
        """
        执行 JavaScript 脚本。
        :param script: 要执行的 JavaScript 代码
        """
        self.page().runJavaScript(script)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if Qt.KeyboardModifier.ControlModifier:
            if event.modifiers():
                position = self.get_cursor_position()
                line = position["lineNumber"]
                index = position["column"]
                jedi_lib = JdeiLib(source=self.text(), filename=self.file_path)
                jump_info = {
                    "assign_addr": jedi_lib.getAssignment(line, index),
                    "reference_addr": jedi_lib.getReferences(line, index),
                }
                self.ctrl_left_click_signal.emit(jump_info)

    def code_run(self):
        # TODO 移回IDE项目重新打通
        # runner = PythonExecutor()
        # runner.execute_file(self.current_file_path)
        # log = runner.stdout
        # error = runner.stderr
        # returncode = runner.returncode
        # self.code_execut_signal.emit((log, error, returncode))
        pass

    def reformat(self):
        """
        使用 autopep8 格式化代码，并在格式化后保持光标位置。
        """
        # 获取当前光标位置
        cursor_position = self.get_cursor_position()
        if cursor_position is None:
            print("无法获取光标位置，跳过格式化操作")
            return

        # 格式化代码
        formatted_code = autopep8.fix_code(self.text())

        # 更新编辑器内容
        self.setText(formatted_code)

        # 获取旧光标行列
        old_line = cursor_position["lineNumber"]
        old_column = cursor_position["column"]

        # 跳转回光标位置
        new_code_lines = formatted_code.splitlines()
        total_lines = len(new_code_lines)

        # 确保行号有效
        line_to_jump = min(old_line, total_lines)
        column_to_jump = min(old_column, len(new_code_lines[line_to_jump - 1]) + 1)  # 列号范围校验

        # 设置光标位置
        self.jump_to_position(line_to_jump, column_to_jump)

    def get_completion_items(self):
        cursor_position = self.get_cursor_position()
        line = cursor_position["lineNumber"]
        index = cursor_position["column"]

        jedi_lib = JdeiLib(source=self.text(), filename=self.file_path)
        completion_lists = jedi_lib.getCompletions(line, index)
        self.add_completion_items(completion_lists)

    def add_completion_items(self, completion_items: list):
        """
        添加代码补全提示项到 Monaco Editor。
        :param completion_items: 补全提示项列表，每个项是一个字典，包含以下键：
            - label: 提示项的显示文本
            - kind: 提示项的类型（例如 function, variable 等）
            - insertText: 插入的文本
            - detail: 提示项的详情
            - documentation: 提示项的文档说明
        """
        js_code = f"""
        (function() {{
            const completionItems = {completion_items};
            monaco.languages.registerCompletionItemProvider(
                editor.getModel().getLanguageId(),
                {{
                    provideCompletionItems: function(model, position) {{
                        const suggestions = completionItems.map(item => {{
                            return {{
                                label: item.label,
                                kind: monaco.languages.CompletionItemKind[item.kind || 'Text'],
                                insertText: item.insertText,
                                detail: item.detail || '',
                                documentation: item.documentation || ''
                            }};
                        }});
                        return {{ suggestions }};
                    }}
                }}
            );
        }})();
        """
        self._execute_script(js_code)
