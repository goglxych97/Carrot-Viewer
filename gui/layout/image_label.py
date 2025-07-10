# gui/layout/image_label.py
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QSizePolicy,
    QPushButton,
    QWidget,
)

from PyQt5.QtCore import Qt, pyqtSignal
import os
import numpy as np
from PyQt5.QtGui import QImage, QPixmap, QIcon


from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QWidget
from PyQt5.QtGui import QFont


class LabelContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("LabelContainer")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            """QWidget#LabelContainer {
            background: #dedede;
            border: 1px solid #aaa;
        }"""
        )
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.layout.setSpacing(4)

    def add_folder_button(self, folder_path: str, callback):
        folder_name = os.path.basename(folder_path)
        button = QPushButton(folder_name)
        button.setStyleSheet("padding: 4px;")
        button.setFont(QFont("Arial", 10))
        button.clicked.connect(lambda: callback(folder_path))
        self.layout.addWidget(button)
