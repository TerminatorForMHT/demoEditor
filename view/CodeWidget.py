from PyQt6.QtCore import QDir, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from qfluentwidgets import TabBar

from config.config import SEP
from view.Editor import Editor


class CodeWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.load_file_dict = dict()
        self.tab_texts = list()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.tab_bar = TabBar()
        self.tab_bar.setAddButtonVisible(False)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet('margin: 2px;')

        self.layout.addWidget(self.tab_bar)
        self.layout.addWidget(self.stacked_widget)

        # self.tab_bar.tabCloseRequested.connect(self.close_tab)
        # self.tab_bar.tabBarClicked.connect(self.switch_tab)

    def load_file(self, file_path):
        # TODO 加上读取文件内容的方法
        self.add_new_tab(file_path)

    def add_new_tab(self, file_path):
        if file_path not in self.load_file_dict.keys():
            editor = Editor(self)
            # TODO 交互桥还需要编写代码跳转信号与代码运行等信号然后挂钩
            self.stacked_widget.addWidget(editor)
            index = self.stacked_widget.count() - 1

            tab_text = file_path.split(SEP)[-1]
            if tab_text in self.tab_texts:
                self.tab_texts.append(tab_text)
                tab_text = f'{file_path.split(SEP)[-2]}{SEP}{tab_text}'
                self.tab_bar.addTab(file_path, tab_text)
            else:
                self.tab_texts.append(tab_text)
                self.tab_bar.addTab(file_path, tab_text)
            self.tab_bar.setCurrentTab(file_path)
            self.stacked_widget.setCurrentWidget(editor)
            self.load_file_dict[file_path] = index
            return editor
        else:
            index = self.load_file_dict.get(file_path)
            self.tab_bar.setCurrentTab(file_path)
            self.stacked_widget.setCurrentIndex(index)
            editor = self.stacked_widget.currentWidget()
            return editor
