from PyQt5.QtWidgets import QWidget, QLabel, QScrollBar, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
import numpy as np


def load_stylesheet(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class InitViewer(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self.setAttribute(Qt.WA_StyledBackground, True)

    def _init_ui(self):
        self.label_container = QWidget()
        self.scroll_container = QWidget()

    def _set_view_type(self, view_type: str):
        if view_type not in ["axial", "coronal", "sagittal"]:
            raise ValueError("Invalid view type")


class SliceViewer(QWidget):
    def __init__(self, tensor: np.ndarray, view_type: str):
        super().__init__()

        self.tensor = tensor
        self.view_type = view_type
        self.axis = self._get_axis(view_type)  # return 값 0,1,2
        self.num_slices = tensor.shape[self.axis]
        self.current_index = self.num_slices // 2
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label_container = QWidget()
        label_layout = QHBoxLayout(self.label_container)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(0)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        label_layout.addWidget(self.label)

        self.label_container.setStyleSheet("background-color: black;")

        self.scroll_container = QWidget()
        self.scroll_container.setStyleSheet(load_stylesheet("styles/scrollbar.css"))
        self.scrollbar = QScrollBar(Qt.Vertical)
        self.scroll_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(self.num_slices - 1)
        self.scrollbar.setValue(self.current_index)
        self.scrollbar.valueChanged.connect(self._update_slice)

        scroll_layout = QHBoxLayout(self.scroll_container)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(2)
        scroll_layout.addWidget(self.scrollbar)

        layout.addWidget(self.label_container)
        layout.addWidget(self.scroll_container)
        QTimer.singleShot(0, lambda: self._update_slice(self.current_index))

    def _get_axis(self, view_type):
        return {"axial": 2, "coronal": 1, "sagittal": 0}[view_type]

    def _update_slice(self, index=None):
        if index is not None:
            self.current_index = index
        img = (
            (self.tensor[:, :, self.current_index])
            if self.view_type == "axial"
            else (
                (self.tensor[:, self.current_index, :])
                if self.view_type == "coronal"
                else (
                    (self.tensor[self.current_index, :, :])
                    if self.view_type == "sagittal"
                    else (_ for _ in ()).throw(ValueError("Invalid view type"))
                )
            )
        )
        img = np.rot90(np.flip(img, axis=0))

        pixmap = self._numpy_to_pixmap(img)
        scaled = pixmap.scaled(
            self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.label.setPixmap(scaled)

    def _numpy_to_pixmap(self, arr):
        norm = (arr - arr.min()) / (arr.ptp() + 1e-5) * 255
        img = norm.astype(np.uint8)
        h, w = img.shape
        qimg = QImage(img.tobytes(), w, h, w, QImage.Format_Grayscale8)
        return QPixmap.fromImage(qimg)

    def _set_view_type(self, view_type: str):
        if view_type not in ["axial", "coronal", "sagittal"]:
            raise ValueError("Invalid view type")

        self.view_type = view_type
        self.axis = self._get_axis(view_type)
        self.num_slices = self.tensor.shape[self.axis]
        self.current_index = self.num_slices // 2

        self.label.repaint()  # 즉시 다시 그림

        try:
            self.scrollbar.valueChanged.disconnect(self._update_slice)
        except TypeError:
            pass
        self.scrollbar.setMaximum(self.num_slices - 1)
        self.scrollbar.setValue(self.current_index)
        self.scrollbar.valueChanged.connect(self._update_slice)

        # 이미지 업데이트
        self._update_slice(self.current_index)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0 and self.current_index > 0:
            self.scrollbar.setValue(self.current_index - 1)
        elif delta < 0 and self.current_index < self.num_slices - 1:
            self.scrollbar.setValue(self.current_index + 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_slice(self.current_index)
