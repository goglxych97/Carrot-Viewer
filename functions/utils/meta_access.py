import os


def type_checking(path):
    if not os.path.isfile(path):
        return False

    try:
        with open(path, "rb") as f:
            header = f.read(352)
        nifti_magic = header[344:348]
        if nifti_magic in [b"n+1\x00", b"ni1\x00"]:
            return "nifti"

        elif header.startswith(b"\x1f\x8b"):
            import gzip

            with gzip.open(path, "rb") as f:
                gz_header = f.read(352)
                gz_magic = gz_header[344:348]
                if gz_magic in [b"n+1\x00", b"ni1\x00"]:
                    return "nifti"

        if header[128:132] == b"DICM":
            return "dicom"

    except Exception as e:
        pass

    return False
