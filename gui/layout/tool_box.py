from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QPushButton,
    QComboBox,
    QListView,
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
import json

from gui.dialog.ai_solution import AISolutionDialog


class ClickableLabel(QLabel):
    clicked = pyqtSignal(int)

    def __init__(self, index):
        super().__init__()
        self.index = index
        self.setFixedSize(32, 32)
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)


class ToolBox(QWidget):
    view_changed = pyqtSignal(str)

    def __init__(self, view_type="axial"):
        super().__init__()
        self.setObjectName("ToolContainer")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.view_type = view_type
        self.labels = []
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet(
            """
            QWidget#ToolContainer {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgb(210, 210, 210), stop:1 rgb(200, 200, 200));
            }
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft)

        self.menu_container = ImportSaveContainer()
        self.info_container = DropDownContainer(json_path="gui/layout/dropdown.json")
        self.icon_container = IconContainer(view_type=self.view_type)
        self.icon_container.view_changed.connect(self._on_view_type_changed)

        self.menu_container.setFixedWidth(130)
        self.info_container.setFixedWidth(338)
        self.icon_container.setMinimumWidth(132)
        self.icon_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.menu_container.import_clicked.connect(self._on_import_clicked)
        self.menu_container.save_clicked.connect(self._on_save_clicked)

        layout.addWidget(self.menu_container)
        layout.addWidget(self.info_container)
        layout.addWidget(self.icon_container)

    def _on_view_type_changed(self, view_type):
        self.view_type = view_type
        self.view_changed.emit(view_type)

    def _on_import_clicked(self):
        print("Import button clicked")

    def _on_save_clicked(self):
        print("Save button clicked")


class IconContainer(QWidget):
    view_changed = pyqtSignal(str)

    def __init__(self, view_type="axial"):
        super().__init__()
        self.view_type = view_type
        self.labels = []
        self._init_ui()

    def _init_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.setAlignment(Qt.AlignLeft)

        image_paths = [
            "images/icon/interpolation.png",
            "images/icon/distance.png",
            "images/icon/cursor.png",
            "images/icon/segment.png",
            "images/icon/axial.png",
            "images/icon/sagittal.png",
            "images/icon/coronal.png",
            "images/icon/grid.png",
        ]

        for idx in range(8):
            i, j = idx // 4, idx % 4
            label = ClickableLabel(idx)
            label.setProperty("selected", False)
            label.setStyleSheet(
                """
                QLabel {
                    padding: 2px;
                }
                QLabel:hover {
                    background-color: #d0d0d0;
                    border: 1px solid #666;
                }
                """
            )
            label.clicked.connect(self._on_icon_clicked)

            pixmap = QPixmap(image_paths[idx])
            if not pixmap.isNull():
                label.setPixmap(pixmap)

            self.labels.append(label)
            layout.addWidget(label, i, j)

        self._highlight_selected_icon(self.view_type)

    def _highlight_selected_icon(self, view_type):
        view_type_to_idx = {"axial": 4, "sagittal": 5, "coronal": 6, "grid": 7}
        highlight_idx = view_type_to_idx.get(view_type, -1)

        for i, label in enumerate(self.labels):
            is_selected = i == highlight_idx
            label.setProperty("selected", is_selected)

            style = """
                QLabel {
                    padding: 2px;
                }
                QLabel:hover {
                    background-color: #d0d0d0;
                    border: 1px solid rgb(164,164,164);
                }
                """
            if is_selected:
                style += """
                    QLabel {
                        background-color: rgba(0, 0, 0, 50);
                        border: 1px solid rgb(164,164,164);
                    }
                    """
            label.setStyleSheet(style)
            label.style().unpolish(label)
            label.style().polish(label)

    def _on_icon_clicked(self, index):
        if index not in [4, 5, 6]:
            return

        view_type_map = {
            4: "axial",
            5: "sagittal",
            6: "coronal",
        }

        new_view_type = view_type_map.get(index)
        if new_view_type == self.view_type:
            return

        self.view_type = new_view_type

        for i in range(4, 7):
            self.labels[i].setProperty("selected", False)
        self.labels[index].setProperty("selected", True)

        self._highlight_selected_icon(new_view_type)
        self.view_changed.emit(new_view_type)


class ImportSaveContainer(QWidget):
    import_clicked = pyqtSignal()
    save_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        button_style = """
            QPushButton {
                padding: 2px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
                border: 1px solid #666;
            }
        """

        self.import_btn = QPushButton()
        self.import_btn.setIcon(QIcon("images/icon/import.png"))
        self.import_btn.setIconSize(QSize(44, 44))
        self.import_btn.setFixedSize(52, 52)
        self.import_btn.setToolTip("Import")
        self.import_btn.setStyleSheet(button_style)
        self.import_btn.clicked.connect(self.import_clicked.emit)

        self.save_btn = QPushButton()
        self.save_btn.setIcon(QIcon("images/icon/save.png"))
        self.save_btn.setIconSize(QSize(44, 44))
        self.save_btn.setFixedSize(52, 52)
        self.save_btn.setToolTip("Save")
        self.save_btn.setStyleSheet(button_style)
        self.save_btn.clicked.connect(self.save_clicked.emit)

        layout.addWidget(self.import_btn)
        layout.addWidget(self.save_btn)


class DropDownContainer(QWidget):
    def __init__(self, json_path="dropdown_options.json", parent=None):
        super().__init__(parent)
        self.setObjectName("InfoDropdownPanel")
        self.setStyleSheet(self._get_stylesheet())

        self.dropdown1 = self._create_dropdown()
        self.dropdown2 = self._create_dropdown()
        self.open_button = self._create_button()

        self._init_ui()
        self._load_dropdown_options(json_path)

    def _create_dropdown(self):
        combo = QComboBox()
        combo.setFixedHeight(20)
        combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        combo.setInsertPolicy(QComboBox.NoInsert)
        combo.setModelColumn(0)

        view = QListView()
        view.setUniformItemSizes(True)
        view.setStyleSheet(
            """
            QListView::item {
                padding: 2px;
            }
            QListView::item:selected {
                background-color: #e6f0fa;
                color: black;
            }
            QListView::item:hover {
                background-color: #f0f0f0;
            }
        """
        )
        combo.setView(view)

        return combo

    def _init_ui(self):
        layout = QVBoxLayout(self)
        top_row = QHBoxLayout()
        top_row.addWidget(self.dropdown1)
        top_row.addWidget(self.dropdown2)
        layout.addLayout(top_row)
        layout.addWidget(self.open_button)
        layout.setContentsMargins(6, 0, 12, 0)
        layout.setSpacing(0)

    def _load_dropdown_options(self, json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.dropdown1.addItems(data.get("dropdown1", []))
            self.dropdown2.addItems(data.get("dropdown2", []))
        except Exception as e:
            print(f"드롭다운 JSON 파일 로딩 실패: {e}")

    def _get_stylesheet(self):
        return """
        QWidget#InfoDropdownPanel {
            background-color: #f4f4f4;
            border: 1px solid #cccccc;
            border-radius: 6px;
        }

        QComboBox {
            background-color: white;
            border: 1px solid #bbbbbb;
            border-radius: 4px;
            padding-left: 6px;       /* 텍스트 왼쪽 여백 */
            padding-right: 20px;     /* 드롭다운 버튼 여백 */
            font-size: 10px;
            height: 22px;
        }

        QComboBox:hover {
            border: 1px solid #999999;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 16px;
            border-left: 1px solid #bbbbbb;
        }

        QComboBox::down-arrow {
            width: 10px;
            height: 10px;
        }

        QListView::item {
            padding: 4px 6px;
            min-height: 18px;
            font-size: 10px;
        }

        QListView::item:selected {
            background-color: #e6f0fa;
            color: black;
        }

        QListView::item:hover {
            background-color: #f0f0f0;
        }
        """

    def _create_button(self):
        button = QPushButton("AI solution")
        button.setFixedHeight(22)  # QComboBox와 동일한 높이
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: 1px solid #bbbbbb;
                border-radius: 4px;
                padding-left: 6px;
                padding-right: 6px;
                font-size: 10px;
            }
            QPushButton:hover {
                border: 1px solid #999999;
                background-color: #f0f0f0;
            }
        """
        )
        button.clicked.connect(self._open_popup)
        return button

    def _open_popup(self):
        dialog = AISolutionDialog(self.dropdown1, self.dropdown2, self)
        dialog.exec_()
