from PyQt5.QtWidgets import (
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from gui.layout.image_panel import SliceViewer, InitViewer
from gui.layout.image_label import LabelContainer
from gui.layout.tool_box import ToolBox
import numpy as np

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap


class ClickableThumbnail(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, key, pixmap):
        super().__init__()
        self.key = key
        self.setFixedSize(120, 130)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setScaledContents(False)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setProperty("selected", False)
        self.update_style()

    def mousePressEvent(self, event):
        self.clicked.emit(self.key)

    def set_selected(self, selected: bool):
        self.setProperty("selected", selected)
        self.update_style()

    def update_style(self):
        if self.property("selected"):
            self.setStyleSheet(
                """
                QLabel {
                    border: 3px solid yellow;
                    margin: 1px;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                QLabel {
                    border: 1px solid transparent;
                    margin: 2px;
                }
            """
            )


class ScrollAreaOnHover(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 스크롤 휠 초기 숨김
        self.setStyleSheet(
            """
            QScrollBar:vertical {
                background: transparent;
                width: 0px;
            }
            """
        )

    def enterEvent(self, event):  # 마우스가 들어오면 필요 시 스크롤바 보이게 함
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet(
            """
            QScrollBar:vertical {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 1, y2: 0,
                    stop: 0 rgb(224, 224, 224),
                    stop: 0.5 rgb(232, 232, 232),
                    stop: 1 rgb(224, 224, 224)
                );
                width: 8;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgb(248, 248, 248);
                border: 0.5px solid rgb(160, 160, 160);  /* 테두리 추가 */
            }
            """
        )
        super().enterEvent(event)

    def leaveEvent(self, event):  # 마우스 나가면 다시 숨김
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(
            """
            QScrollBar:vertical {
                background: transparent;
                width: 0px;
            }
            """
        )
        super().leaveEvent(event)

    def wheelEvent(self, event):
        if self.underMouse():
            super().wheelEvent(event)
        else:
            event.ignore()


class LeftContainer(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self.thumbnails = {}  # key: path → ClickableThumbnail

    def clear(self):
        for thumb in self.thumbnails.values():
            thumb.deleteLater()
        self.thumbnails.clear()
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _init_ui(self):
        layout = QVBoxLayout(self)  # 전체 레이아웃
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        scroll_area = ScrollAreaOnHover(self)  # 스크롤 영역 생성
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_content = QWidget()  # 스크롤 내부 컨텐츠 위젯
        scroll_content.setStyleSheet(
            """
            background-color: black;
            border : none;
            """
        )
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(4, 4, 4, 4)
        self.scroll_layout.setSpacing(5)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        scroll_content.setLayout(self.scroll_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def _add_thumbnail(self, img_array, key, callback):
        # 1. 정규화 및 QPixmap 생성
        norm = (img_array - img_array.min()) / (img_array.ptp() + 1e-5) * 255
        img = norm.astype(np.uint8)
        h, w = img.shape[:2]
        qimg = QImage(img.tobytes(), w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)
        scaled_pixmap = pixmap.scaled(
            120, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # 2. 썸네일 생성 및 이벤트 연결
        thumbnail = ClickableThumbnail(key, QPixmap())  # 먼저 빈 Pixmap으로 초기화
        thumbnail.setPixmap(scaled_pixmap)  # 이미지는 여기서 설정
        thumbnail.clicked.connect(callback)

        # 3. 썸네일 표시
        self.scroll_layout.addWidget(thumbnail)
        self.thumbnails[key] = thumbnail

    # def _add_thumbnail(self, img_array):  # 썸네일은 min-max normalization
    #     thumbnail = QLabel()
    #     thumbnail.setFixedSize(120, 130)
    #     thumbnail.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    #     thumbnail.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    #     thumbnail.setScaledContents(False)

    #     norm = (img_array - img_array.min()) / (img_array.ptp() + 1e-5) * 255
    #     img = norm.astype(np.uint8)
    #     h, w = img.shape
    #     qimg = QImage(img.tobytes(), w, h, w, QImage.Format_Grayscale8)
    #     pixmap = QPixmap.fromImage(qimg)
    #     scaled_pixmap = pixmap.scaled(
    #         thumbnail.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
    #     )
    #     thumbnail.setPixmap(scaled_pixmap)
    #     self.scroll_layout.addWidget(thumbnail)


class RightContainer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label_container = LabelContainer()

        self.grid_container = QWidget()
        self.grid_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        grid_layout = QVBoxLayout(self.grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)

        self.slice_container = InitViewer()
        self.slice_container.setStyleSheet("background: black;")
        grid_layout.addWidget(self.slice_container)

        layout.addWidget(self.label_container)
        layout.addWidget(self.grid_container)
