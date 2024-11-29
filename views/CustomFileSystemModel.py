from PyQt6.QtGui import QFileSystemModel


class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        pass
