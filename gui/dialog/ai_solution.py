from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QWidget,
    QFrame,
    QSizePolicy,
    QComboBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class SkullStrippingDetailWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: #f5f5f5; padding: 8px; margin: 4px 0;")
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # 우측 텍스트와 이미지
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("<b>Brain Skull Stripping</b>")
        title.setStyleSheet("font-size: 14px; margin: 0px;")
        content_layout.addWidget(title)

        # Links
        links = QLabel()
        links.setTextFormat(Qt.RichText)
        links.setText(
            '<a href="https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/BET">📄 Documentation</a> &nbsp;&nbsp; '
            '<a href="https://github.com/aramis-lab/clinicadl/blob/main/clinicadl/pipelines/preprocessing/skull_stripping.py">💻 Source Code</a>'
        )
        links.setOpenExternalLinks(True)
        links.setStyleSheet("margin: 0px;")
        content_layout.addWidget(links)

        # Description
        desc = QLabel(
            "This task removes non-brain tissues from 3D T1-weighted MRI using a UNet-based model. For 3D volumes, the model treats them as a stack of 2D slices. This model generates a probability map, which is subsequently converted into a binary mask through thresholding."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("margin: 0px;")
        content_layout.addWidget(desc)

        # Input
        input_label = QLabel("<b>Input:</b> 3D T1-weighted MRI — shape: (512, 512)")
        input_label.setStyleSheet("margin: 0px;")
        content_layout.addWidget(input_label)

        # Output
        output_label = QLabel(
            "<b>Output:</b> Skull-stripped binary mask — shape: (512, 512)"
        )
        output_label.setStyleSheet("margin: 0px;")
        content_layout.addWidget(output_label)

        # Example Image
        img_label = QLabel()
        pixmap = QPixmap("assets/skull_stripping_example.png")
        if not pixmap.isNull():
            img_label.setPixmap(pixmap.scaledToWidth(280, Qt.SmoothTransformation))
            img_label.setStyleSheet("margin: 4px 0px;")
            content_layout.addWidget(img_label)
        layout.addLayout(content_layout, 4)

        # 우측 버튼 그룹
        button_col = QVBoxLayout()
        button_col.setAlignment(Qt.AlignTop | Qt.AlignRight)
        run_button = QPushButton("Run")
        chat_button = QPushButton("Chat")

        for btn in (run_button, chat_button):
            btn.setStyleSheet(
                "background-color: #0078d7; color: white; padding: 4px 10px; border-radius: 3px; font-weight: bold;"
            )
            btn.setFixedWidth(90)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            button_col.addWidget(btn)

        layout.addLayout(button_col, 1)


class AISolutionDialog(QDialog):
    def __init__(self, dropdown1_ref, dropdown2_ref, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Solution Search")
        self.setMinimumSize(800, 500)
        self.dropdown1 = dropdown1_ref
        self.dropdown2 = dropdown2_ref
        self.detail_widget = None  # 동적 상세 설명 위젯
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 상단 드롭다운 정보 표시
        label_layout = QHBoxLayout()

        self.body_label = QLabel("Body Part:")
        self.body_value = QComboBox()
        self.body_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._sync_combobox(self.body_value, self.dropdown1)
        label_layout.addWidget(self.body_label)
        label_layout.addWidget(self.body_value)

        self.modality_label = QLabel("Modality:")
        self.modality_value = QComboBox()
        self.modality_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._sync_combobox(self.modality_value, self.dropdown2)
        label_layout.addWidget(self.modality_label)
        label_layout.addWidget(self.modality_value)

        layout.addLayout(label_layout)

        self.dropdown1.currentIndexChanged.connect(self._update_info_label)
        self.dropdown2.currentIndexChanged.connect(self._update_info_label)

        # 검색창
        search_row = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Please enter your keyword(s) to search.")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._on_search_clicked)
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_button)
        layout.addLayout(search_row)

        # 스크롤 영역
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.result_container)
        layout.addWidget(self.scroll_area)

        # 예시 키워드 리스트
        self.ai_tasks = [
            "Brain Skull Stripping",
            "Brain Tumor Segmentation (BraTS 2021)",
            "White Matter Hyperintensity Segmentation",
            "Perivascular Space Segmentation",
            "Superior Sagittal Sinus Segmentation",
        ]

        for task in self.ai_tasks:
            item = self._create_result_item(task)
            self.result_layout.addWidget(item)

    def _sync_combobox(self, target_combo, source_combo):
        for i in range(source_combo.count()):
            target_combo.addItem(source_combo.itemText(i))
        target_combo.setCurrentIndex(source_combo.currentIndex())

    def _update_info_label(self):
        self.body_value.setCurrentIndex(self.dropdown1.currentIndex())
        self.modality_value.setCurrentIndex(self.dropdown2.currentIndex())

    def _on_search_clicked(self):
        query = self.search_input.text()
        print(f"검색어: {query}")
        # 실제 검색 기능 구현 필요

    def _create_result_item(self, title):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(frame)

        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(label)

        label.mousePressEvent = lambda e: self._show_detail(title, frame)
        return frame

    def _show_detail(self, title, parent_widget):
        if self.detail_widget:
            self.result_layout.removeWidget(self.detail_widget)
            self.detail_widget.deleteLater()
            self.detail_widget = None

        if title == "Brain Skull Stripping":
            detail = SkullStrippingDetailWidget()
        else:
            detail = QFrame()
            detail.setFrameShape(QFrame.StyledPanel)
            detail.setStyleSheet(
                "background-color: #f5f5f5; padding: 8px; margin: 5px 0;"
            )
            layout = QVBoxLayout(detail)
            label = QLabel(f"Selected task: {title}")
            layout.addWidget(label)

        index = self.result_layout.indexOf(parent_widget)
        self.result_layout.insertWidget(index + 1, detail)
        self.detail_widget = detail
