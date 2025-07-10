from PyQt5.QtWidgets import QMenuBar


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_menus()

    def _create_menus(self):
        file_menu = self.addMenu("File")
        edit_menu = self.addMenu("Edit")
        tool_menu = self.addMenu("Tools")
        help_menu = self.addMenu("Help")
