from nibabel.orientations import (
    axcodes2ornt,
    io_orientation,
    ornt_transform,
    apply_orientation,
)
import nibabel as nib
import numpy as np
import os


def reorient_to_RAS(img):
    arr = img.get_fdata()
    orig_ornt = io_orientation(img.affine)  # 현재 방향
    target_ornt = axcodes2ornt(("R", "A", "S"))  # 이미지 회전
    transform = ornt_transform(orig_ornt, target_ornt)
    reoriented = apply_orientation(arr, transform)
    return reoriented


def load_nifti_array(path: str):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File does not exist: {path}")
    try:
        nii_img = nib.load(path)
        header = nii_img.header
        affine = nii_img.affine
        tensor = reorient_to_RAS(nii_img)
        if tensor.ndim == 4 and tensor.shape[-1] == 1:
            tensor = np.squeeze(tensor, axis=-1)
        elif tensor.ndim == 4 and tensor.shape[0] == 1:
            tensor = np.squeeze(tensor, axis=0)
        return tensor, header, affine

    except Exception as e:
        raise RuntimeError(f"Failed to load NIfTI file: {e}")
