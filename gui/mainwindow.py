from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from gui.layout.image_panel import SliceViewer
from gui.layout.containers import LeftContainer, RightContainer
from gui.layout.image_label import LabelContainer
from gui.layout.tool_box import ToolBox
from gui.layout.menus import MenuBar
from PyQt5.QtGui import QIcon
import numpy as np
from functions.io.file_loader import load_nifty, load_dicom
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.view_type = "axial"  # view type / default="axial"
        self.setMenuBar(MenuBar(self))  # 메뉴 바 설정
        self._init_ui()  # ui 셋업
        self.setAcceptDrops(True)  # drag & drop 허용
        self.study_dicts = {}  # 로드된 이미지 저장
        # local 파라미터
        self.view_type = "axial"
        self.interp_check = True
        self.study_dicts = {}  # key: path, value: {tensor, header, affine, folder}
        self.label_groups = {}  # key: folder path, value: list of file paths
        self.label_containers = {}  # key: folder path, value: LabelContainer instance

    def _init_ui(self):
        self.setWindowTitle("Carrot Viewer")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setMinimumSize(600, 480)  # 최소 사이즈
        self.setGeometry(
            100, 100, 800, 640
        )  # 프로그램 시작 위치 (100, 100), 시작 사이즈(800, 640)
        self.main_container = QWidget()  # Main widget
        self.main_container.setObjectName("MainContainer")
        self.main_container.setAttribute(Qt.WA_StyledBackground, True)
        self.main_container.setStyleSheet(
            """
            #MainContainer {
                background-color: rgb(236,236,236);
            }
            """
        )
        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.tool_container = ToolBox()  # 최상단 컨테이너
        self.tool_container.setFixedHeight(65)
        content_container = QWidget()  # 좌우 컨테이너 묶음
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.setAlignment(Qt.AlignLeft)
        self.left_container = LeftContainer()
        self.right_container = RightContainer()
        self.left_container.setFixedWidth(130)
        self.left_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.right_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout.addWidget(self.left_container)
        content_layout.addWidget(self.right_container)
        main_layout.addWidget(self.tool_container)
        main_layout.addWidget(content_container)
        self.setCentralWidget(self.main_container)
        self.tool_container.view_changed.connect(self._update_view_type)

    def _update_view_type(self, view_type):
        self.view_type = view_type
        viewer = self.right_container.slice_container
        if isinstance(viewer, SliceViewer):
            viewer._set_view_type(view_type)

    def _update_interp_type(self, interp_type):
        self.interp_type = interp_type

    def _update_viewer_instance(self, instance):
        grid_layout = self.right_container.grid_container.layout()
        old_viewer = self.right_container.slice_container
        grid_layout.addWidget(instance)
        grid_layout.removeWidget(old_viewer)
        old_viewer.deleteLater()
        instance.show()
        self.right_container.slice_container = instance

    def _update_thmbnail_box(self, img_tensor):
        ndim = img_tensor.ndim
        if ndim == 2:
            img_thmb = img_tensor
        else:
            slicing = [slice(None)] * 2
            slicing.append(img_tensor.shape[2] // 2)
            slicing += [0] * (ndim - len(slicing))
            img_thmb = img_tensor[tuple(slicing)]
        img_thmb = np.rot90(np.flip(img_thmb, axis=0))
        self.left_container._add_thumbnail(img_thmb)

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # def dropEvent(self, event):
    #     urls = event.mimeData().urls()
    #     if not urls:
    #         return

    #     for url in urls:
    #         path = url.toLocalFile()
    #         try:
    #             image_data = load_nifty(path)
    #         except Exception as e:
    #             print(f"[Error] Failed to load image: {e}")
    #             continue

    #         self.study_dicts[path] = image_data
    #         folder = image_data["folder"]
    #         self.label_groups.setdefault(folder, []).append(path)

    #         if folder not in self.label_containers:
    #             label = LabelContainer()
    #             label.add_folder_button(folder, callback=self._on_label_clicked)
    #             self.label_containers[folder] = label
    #             self.right_container.label_container.layout.addWidget(label)

    #         self._on_label_clicked(folder)
    #         self._on_thumbnail_clicked(path)

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return

        for url in urls:
            path = url.toLocalFile()
            try:
                if os.path.isfile(path):
                    # --- NIfTI 처리 ---
                    image_data = load_nifty(path)
                    key = path
                    folder = image_data["folder"]

                    self.study_dicts[key] = image_data
                    self.label_groups.setdefault(folder, []).append(key)

                    if folder not in self.label_containers:
                        label = LabelContainer()
                        label.add_folder_button(folder, callback=self._on_label_clicked)
                        self.label_containers[folder] = label
                        self.right_container.label_container.layout.addWidget(label)

                    self._on_label_clicked(folder)
                    self._on_thumbnail_clicked(key)

                elif os.path.isdir(path):
                    # --- DICOM 처리 ---
                    image_list = load_dicom(path)
                    for image_data in image_list:
                        key = image_data["key"]
                        folder = image_data["folder"]

                        self.study_dicts[key] = image_data
                        self.label_groups.setdefault(folder, []).append(key)

                        if folder not in self.label_containers:
                            label = LabelContainer()
                            label.add_folder_button(
                                folder, callback=self._on_label_clicked
                            )
                            self.label_containers[folder] = label
                            self.right_container.label_container.layout.addWidget(label)

                        self._on_label_clicked(folder)
                        self._on_thumbnail_clicked(key)

                else:
                    raise ValueError("Invalid drop item: not a file or directory.")

            except Exception as e:
                print(f"[Error] Failed to load image: {e}")
                continue

    def _on_label_clicked(self, folder: str):
        self.left_container.clear()

        paths = self.label_groups.get(folder, [])
        for path in paths:
            img_tensor = self.study_dicts[path]["tensor"]
            thumbnail_img = self._safe_extract_slice(img_tensor)
            self.left_container._add_thumbnail(
                thumbnail_img,
                key=path,
                callback=lambda key=path: self._on_thumbnail_clicked(key),
            )

        if paths:
            self._on_thumbnail_clicked(paths[0])  # 가장 앞에 있는 이미지 자동 표시

    def _safe_extract_slice(self, img_tensor):
        if img_tensor.ndim == 2:
            return np.rot90(np.flip(img_tensor, axis=0))
        elif img_tensor.ndim == 3:
            index = img_tensor.shape[2] // 2
            return np.rot90(np.flip(img_tensor[:, :, index], axis=0))
        else:
            raise ValueError("Invalid tensor shape")

    def _on_thumbnail_clicked(self, key: str):
        if key in self.study_dicts:
            item = self.study_dicts[key]
            tensor = item["tensor"]
            instance = SliceViewer(tensor, self.view_type)
            self._update_viewer_instance(instance)

            # 선택 상태 표시
            for path, thumb in self.left_container.thumbnails.items():
                thumb.set_selected(path == key)
