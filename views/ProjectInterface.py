import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QDir, QModelIndex
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSplitter, QWidget, QMessageBox, QHBoxLayout, \
    QInputDialog, QFileDialog
from qfluentwidgets import TreeView, RoundMenu, Action, FluentIcon, DropDownPushButton, MessageBox, Dialog

from config.config import MySettings, ROOT_PATH
from views.CodeWidget import CodeWidget
from views.CustomFileSystemModel import CustomFileSystemModel
from views.InputDialog import InputDialog


class ProjectInterface(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.parent = parent

        self.setObjectName(text.replace(' ', '-'))
        self.history_file = ROOT_PATH / 'conf' / "project_history.json"
        self.project_history = self.load_project_history()
        self.init_ui()

    def init_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.setup_menubar()
        self.set_middle()

    def setup_menubar(self):
        self.top_widget = QWidget()
        self.top_widget.setFixedHeight(50)
        self.top_widget.setFixedWidth(260)
        self.top_layout = QHBoxLayout(self.top_widget)
        self.top_widget.setLayout(self.top_layout)
        self.vBoxLayout.addWidget(self.top_widget)

        self.top_file_button = self.create_menu_button("文件", FluentIcon.FOLDER, [
            ("新建项目", self.create_new_folder),
            ("打开项目", self.open_folder)
        ])
        self.top_layout.addWidget(self.top_file_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.top_project_button = DropDownPushButton(FluentIcon.PROJECTOR, "项目")
        self.project_menu = RoundMenu('项目', self.top_project_button)
        self.top_project_button.setMenu(self.project_menu)
        self.top_layout.addWidget(self.top_project_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.top_layout.setSpacing(0)

    def set_middle(self):
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.file_system_model = CustomFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())

        self.left_widget = QWidget()
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.tree_view = TreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.rootPath()))
        self.tree_view.doubleClicked.connect(self.on_tree_view_double_clicked)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

        for i in range(1, 4):
            self.tree_view.setColumnHidden(i, True)
        left_layout.addWidget(self.tree_view)
        self.splitter.addWidget(self.left_widget)

        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_code = CodeWidget('code widget')
        self.right_code.setStyleSheet("margin: 0px;")
        right_layout.addWidget(self.right_code)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([int(self.width() * 0.1), int(self.width() * 0.9)])
        self.vBoxLayout.addWidget(self.splitter)

    def on_tree_view_double_clicked(self, index):
        if not self.file_system_model.isDir(index):
            file_path = self.file_system_model.filePath(index)
            try:
                self.right_code.load_file(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {file_path}\n{str(e)}")
            # self.open_file_signal.emit()

    def show_context_menu(self, position):
        index = self.tree_view.indexAt(position)
        menu = RoundMenu()
        if not index.isValid():
            menu.addAction(Action(FluentIcon.ADD, "新建文件", triggered=lambda: self.create_item_root("file")))

            menu.addAction(Action(FluentIcon.ADD, "新建文件夹", triggered=lambda: self.create_item_root("folder")))

            menu.addAction(Action(FluentIcon.ADD, "新建Python包", triggered=lambda: self.create_item_root("package")))

            menu.addAction(
                Action(FluentIcon.ADD, "新建Python文件", triggered=lambda: self.create_item_root("python_file")))
        else:

            is_directory = self.file_system_model.isDir(index)

            if is_directory:
                menu.addAction(Action(FluentIcon.ADD, "新建文件", triggered=lambda: self.create_item(index, "file")))

                menu.addAction(
                    Action(FluentIcon.ADD, "新建文件夹", triggered=lambda: self.create_item(index, "folder")))

                menu.addAction(
                    Action(FluentIcon.ADD, "新建Python包", triggered=lambda: self.create_item(index, "package")))

                menu.addAction(
                    Action(FluentIcon.ADD, "新建Python文件", triggered=lambda: self.create_item(index, "python_file")))

            menu.addAction(Action(FluentIcon.DELETE, "删除", triggered=lambda: self.delete_item(index)))

            menu.addAction(Action(FluentIcon.GLOBE, "从本地路径打开", triggered=lambda: self.open_local_path(index)))
        menu.exec(QCursor.pos())

    def create_menu_button(self, text, icon, actions):
        button = DropDownPushButton(icon, text)
        menu = RoundMenu(text, button)
        menu.setIcon(icon)
        for action_text, action_method in actions:
            menu.addAction(Action(icon, action_text, triggered=action_method))
        button.setMenu(menu)
        return button

    def create_new_folder(self):
        index = self.tree_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Warning", "No directory selected!")
            return

        dir_path = self.file_system_model.filePath(index)
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter the name of the new folder:")
        if ok and folder_name:
            QDir(dir_path).mkdir(folder_name)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", QDir.homePath())
        self.project_path = folder_path
        if folder_path:
            self.tree_view.setRootIndex(self.file_system_model.index(folder_path))
            self.add_project_to_history(os.path.basename(folder_path), folder_path)
            self.last_opened_file = folder_path
            MySettings.setValue("project_path", folder_path)
            self.save_settings()

    def load_project_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as file:
                return json.load(file)
        return []

    def open_project(self, path):
        if os.path.exists(path):
            self.project_path = path
            self.tree_view.setRootIndex(self.file_system_model.index(path))
            self.last_opened_file = path
            self.save_settings()
        else:
            QMessageBox.warning(self, "Warning", f"The project path {path} does not exist.")
            self.project_history = [proj for proj in self.project_history if proj['path'] != path]
            self.save_project_history()
            self.display_project_history()

    def save_project_history(self):
        try:
            with open(self.history_file, 'w') as file:
                json.dump(self.project_history, file, indent=4)
        except Exception as e:
            print(e)

    def display_project_history(self):
        self.project_menu.clear()
        for project in self.project_history:
            self.project_menu.addAction(Action(
                FluentIcon.PROJECTOR, project['name'],
                triggered=lambda checked, path=project['path']: self.open_project(path)))

    def add_project_to_history(self, name, path):
        project = {"name": name, "path": path}
        if project not in self.project_history:
            self.project_history.append(project)
            self.save_project_history()
            self.display_project_history()

    def save_settings(self):
        MySettings.setValue("lastProject", self.project_history)
        MySettings.setValue("lastOpenedFile", self.last_opened_file)

    def open_local_path(self, index: QModelIndex):
        file_path_str = self.file_system_model.filePath(index)
        file_path = Path(file_path_str)
        if Path(file_path).exists():
            if sys.platform == "win32":
                command = f'explorer /select,"{file_path}"'
                os.system(command)
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", file_path])
            else:
                os.system(f"xdg-open {file_path}")
        else:
            m_box = MessageBox("错误", "路径不存在!")
            m_box.exec()

    def create_item_root(self, item_type: str):
        file_path = Path(self.project_path)
        input_dialog = InputDialog(f"新建{item_type}", f"输入新{item_type}的名称:", self)

        def func():
            name = input_dialog.urlLineEdit.text()
            if item_type == "folder":
                new_path = Path(file_path) / name
                new_path.mkdir(exist_ok=True)
            elif item_type == "package":
                new_path = Path(file_path) / name
                new_path.mkdir(exist_ok=True)
                init_file = new_path / "__init__.py"
                init_file.touch()
            elif item_type == "python_file":
                new_path = Path(file_path) / f"{name}.py"
                new_path.touch()
            elif item_type == "file":
                new_path = Path(file_path) / name
                new_path.touch()
            else:
                m_box = MessageBox("错误", f"未知的创建类型: {item_type}")
                m_box.exec()
            input_dialog.accept()

        input_dialog.yesButton.clicked.connect(func)
        input_dialog.show()

    def delete_item(self, index):
        file_path_str = self.file_system_model.filePath(index)
        file_path = Path(file_path_str)

        if not file_path.exists():
            w = Dialog("错误", "路径不存在!", self)
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.show()
            if w.exec():
                w.hide()

        x = MessageBox("确认操作", "是否删除？", self)

        if x.exec():
            try:
                if file_path.is_dir():
                    os.rmdir(file_path)
                else:
                    os.remove(file_path)
                self.file_system_model.remove(index)
            except Exception as e:
                log_str = str(e)
                if 'directory not empty' in log_str.lower():
                    y = MessageBox("非空文件夹", "是否删除？", self)
                    if y.exec():
                        shutil.rmtree(file_path)
                    else:
                        y.hide()
                    return
                y = Dialog("错误", f"删除失败: {log_str}", self)
                y.cancelButton.hide()
                y.buttonLayout.insertStretch(1)
                y.show()
                if y.exec():
                    y.hide()
        else:
            x.hide()
