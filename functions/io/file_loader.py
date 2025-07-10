import os
from functions.utils.meta_access import type_checking
from functions.utils.load_file import load_nifti_array

import os
import numpy as np
import pydicom


def load_nifty(path: str):
    file_format = type_checking(path)

    if file_format == "nifti":
        tensor, header, affine = load_nifti_array(path)
        return {
            "type": "nifti",
            "tensor": tensor,
            "header": header,
            "affine": affine,
            "path": path,
            "folder": os.path.dirname(path),
        }

    else:
        raise ValueError(f"Unsupported file type: {file_format}")


# import os
# import pydicom
# import numpy as np
# from collections import defaultdict


# def load_dicom(folder_path: str):
#     if not os.path.isdir(folder_path):
#         raise ValueError("DICOM input must be a folder.")

#     dicom_files = [
#         os.path.join(folder_path, f)
#         for f in os.listdir(folder_path)
#         if f.lower().endswith(".dcm")
#     ]
#     if not dicom_files:
#         raise ValueError("No DICOM files found in the folder.")

#     # 1. 시리즈 UID 기준으로 그룹화
#     series_dict = defaultdict(list)
#     for path in dicom_files:
#         try:
#             dcm = pydicom.dcmread(path, stop_before_pixels=False)
#             series_uid = dcm.SeriesInstanceUID
#             series_dict[series_uid].append((dcm, path))
#         except Exception as e:
#             print(f"[Warning] Failed to read DICOM file {path}: {e}")
#             continue

#     result = []

#     for series_uid, slices in series_dict.items():
#         try:
#             # 2. 동일한 shape만 유지
#             slices = sorted(
#                 [s for s in slices if hasattr(s[0], "PixelData")],
#                 key=lambda x: (
#                     float(x[0].ImagePositionPatient[2])
#                     if hasattr(x[0], "ImagePositionPatient")
#                     else 0
#                 ),
#             )
#             arrays = [s[0].pixel_array for s in slices]
#             shapes = [a.shape for a in arrays]
#             if len(set(shapes)) != 1:
#                 print(f"[Warning] Skipping Series {series_uid} due to shape mismatch")
#                 continue

#             volume = np.stack(arrays, axis=-1)

#             result.append(
#                 {
#                     "type": "dicom",
#                     "tensor": volume,
#                     "series_uid": series_uid,
#                     "folder": os.path.dirname(folder_path),
#                     "key": os.path.join(folder_path, series_uid),
#                     "path_list": [s[1] for s in slices],
#                 }
#             )

#         except Exception as e:
#             print(f"[Error] Failed to process Series {series_uid}: {e}")

#     if not result:
#         raise ValueError("No valid DICOM series found in the folder.")

#     return result
import os
import numpy as np
import pydicom
from collections import defaultdict


def compute_slice_location(dcm):
    """슬라이스의 위치를 normal 벡터 방향으로 투영한 값 반환."""
    orientation = np.array(dcm.ImageOrientationPatient).reshape(2, 3)
    position = np.array(dcm.ImagePositionPatient)
    normal = np.cross(orientation[0], orientation[1])
    location = np.dot(position, normal)
    return location


def load_dicom(folder_path: str):
    if not os.path.isdir(folder_path):
        raise ValueError("DICOM input must be a folder.")

    dicom_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(".dcm")
    ]
    if not dicom_files:
        raise ValueError("No DICOM files found in the folder.")

    series_dict = defaultdict(list)
    for path in dicom_files:
        try:
            dcm = pydicom.dcmread(path, stop_before_pixels=False)
            series_uid = dcm.SeriesInstanceUID
            series_dict[series_uid].append((dcm, path))
        except Exception as e:
            print(f"[Warning] Failed to read DICOM file {path}: {e}")
            continue

    result = []

    for series_uid, slices in series_dict.items():
        try:
            valid_slices = [s for s in slices if hasattr(s[0], "PixelData")]
            valid_slices = sorted(
                valid_slices, key=lambda x: compute_slice_location(x[0])
            )

            arrays = [s[0].pixel_array for s in valid_slices]
            shapes = [a.shape for a in arrays]
            if len(set(shapes)) != 1:
                print(f"[Warning] Skipping Series {series_uid} due to shape mismatch")
                continue

            volume = np.stack(arrays, axis=-1)

            # 방향 확인용 로그
            first_dcm = valid_slices[0][0]
            ori = np.array(first_dcm.ImageOrientationPatient).reshape(2, 3)
            normal = np.cross(ori[0], ori[1])
            print(f"[Info] Series {series_uid} direction normal: {normal}")

            result.append(
                {
                    "type": "dicom",
                    "tensor": volume,
                    "series_uid": series_uid,
                    "folder": os.path.dirname(folder_path),
                    "key": os.path.join(folder_path, series_uid),
                    "path_list": [s[1] for s in valid_slices],
                }
            )

        except Exception as e:
            print(f"[Error] Failed to process Series {series_uid}: {e}")

    if not result:
        raise ValueError("No valid DICOM series found in the folder.")

    return result
