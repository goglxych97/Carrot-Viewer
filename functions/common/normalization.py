import numpy as np


def min_max_normalize(array: np.ndarray, out_range=(0, 255)) -> np.ndarray:
    min_val = array.min()
    max_val = array.max()
    scale = out_range[1] - out_range[0]

    # ptp = peak-to-peak = max - min, but 명시적으로 작성
    norm = (array - min_val) / (max_val - min_val + 1e-5)  # 0~1
    scaled = norm * scale + out_range[0]  # 범위 변환
    return scaled.astype(np.uint8)
