import pathlib
from typing import Literal
import numpy as np
import imageio.v3 as iio
import shutil
import numcodecs


def get_image(image_dir_path: pathlib.Path) -> np.array:
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


def get_numcodec_shuffle(shuffle: Literal["shuffle", "noshuffle", "bitshuffle"]) -> int:
    match shuffle:
        case "shuffle":
            return numcodecs.Blosc.SHUFFLE
        case "noshuffle":
            return numcodecs.Blosc.NOSHUFFLE
        case "bitshuffle":
            return numcodecs.Blosc.BITSHUFFLE
        case _:
            raise ValueError(f"invalid shuffle value for blosc {shuffle}")
