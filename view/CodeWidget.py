from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QMessageBox
from qfluentwidgets import TabBar
from config.config import SEP
from view.Editor import Editor

class CodeWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.load_file_dict = dict()  # 存储文件路径与索引的映射
        self.tab_texts = list()  # 存储已加载的文件Tab文本
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.tab_bar = TabBar()
        self.tab_bar.setAddButtonVisible(False)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)  # 监听关闭Tab事件
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("margin: 2px;")

        self.layout.addWidget(self.tab_bar)
        self.layout.addWidget(self.stacked_widget)

    def load_file(self, file_path):
        """
        加载文件
        :param file_path: 文件路径
        """
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        editor = self.add_new_tab(file_path)
        editor.set_editor_content(content)

    def add_new_tab(self, file_path):
        """
        新增打开文件Tab
        :param file_path: 文件路径
        :return: 新增的编辑器页面
        """
        if file_path not in self.load_file_dict:
            editor = Editor(self)
            # 挂钩信号：跳转到行列信号与代码运行信号
            editor.ctrlClickPosition.connect(self.handle_ctrl_click)
            editor.cursorPositionChanged.connect(self.handle_cursor_change)

            self.stacked_widget.addWidget(editor)
            index = self.stacked_widget.count() - 1

            # Tab文本去重与显示路径
            tab_text = file_path.split(SEP)[-1]
            if tab_text in self.tab_texts:
                tab_text = f"{file_path.split(SEP)[-2]}{SEP}{tab_text}"
            self.tab_texts.append(tab_text)
            self.tab_bar.addTab(file_path, tab_text)

            self.tab_bar.setCurrentTab(file_path)
            self.stacked_widget.setCurrentWidget(editor)
            self.load_file_dict[file_path] = index
            return editor
        else:
            # 文件已加载，切换到对应Tab
            index = self.load_file_dict[file_path]
            self.tab_bar.setCurrentTab(file_path)
            self.stacked_widget.setCurrentIndex(index)
            return self.stacked_widget.currentWidget()

    def close_tab(self, file_path):
        """
        关闭指定Tab，并在关闭前保存文件变更
        :param file_path: 文件路径
        """
        index = self.load_file_dict.get(file_path)
        if index is None:
            return

        # 获取编辑器实例
        editor = self.stacked_widget.widget(index)
        script = """
        (function() {
            return getEditorContent();
        })();
        """
        editor.page().runJavaScript(script, lambda content: self._save_and_close(file_path, content, index))

    def _save_and_close(self, file_path, content, index):
        """
        保存文件并关闭Tab
        :param file_path: 文件路径
        :param content: 编辑器中的内容
        :param index: Tab索引
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
        except Exception as e:
            QMessageBox.critical(self, "保存文件错误", f"保存文件时发生错误：{e}")
            return

        # 移除Tab和对应的编辑器
        self.tab_bar.removeTab(file_path)
        self.stacked_widget.removeWidget(self.stacked_widget.widget(index))
        self.load_file_dict.pop(file_path)
        self.tab_texts.remove(file_path.split(SEP)[-1])

    def handle_ctrl_click(self, line, column):
        """
        处理Ctrl+点击事件
        :param line: 行号
        :param column: 列号
        """
        print(f"Ctrl+Click at Line: {line}, Column: {column}")
        # 在此处添加跳转或处理逻辑

    def handle_cursor_change(self, line, column):
        """
        处理光标位置变化事件
        :param line: 当前行号
        :param column: 当前列号
        """
        print(f"Cursor moved to Line: {line}, Column: {column}")
        # 在此处添加需要响应的逻辑
