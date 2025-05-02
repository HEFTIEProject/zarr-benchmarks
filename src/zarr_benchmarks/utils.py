import os
import pathlib
import shutil

import imageio.v3 as iio
import numpy as np
import numpy.typing as npt


def get_image(image_dir_path: pathlib.Path) -> npt.NDArray:
    """Read a series of jpeg to one 3D numpy array"""
    image_slices = []
    for image_slice in image_dir_path.iterdir():
        if not image_slice.is_file():
            continue

        image_slices.append(iio.imread(image_slice))

    image = np.stack(image_slices, axis=0)

    return image


def remove_output_dir(output_dir: pathlib.Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)


def get_directory_size(path: pathlib.Path) -> int:
    """
    Get total size of a directory in bytes.
    """
    total_size = 0
    if not path.is_dir():
        raise ValueError(f"Path not a directory: {path}")
    for dirpath, dirnames, filenames in path.walk():
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    return total_size
