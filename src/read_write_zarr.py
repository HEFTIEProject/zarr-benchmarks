import imageio.v3 as iio
import pathlib
import numpy as np
import zarr
import shutil


def get_compression_ratio(store_path: pathlib.Path) -> float:
    zarr_array = zarr.open_array(store_path, mode="r")
    compression_ratio = zarr_array.nbytes / zarr_array.nbytes_stored()

    return compression_ratio


def read_zarr_array(store_path: pathlib.Path) -> np.array:
    zarr_read = zarr.open_array(store_path, mode="r")
    read_image = zarr_read[:]
    return read_image


def write_zarr_array(
    image: np.array, store_path: pathlib.Path, overwrite: bool
) -> None:
    if overwrite:
        remove_output_dir(store_path)

    zarr_array = zarr.create_array(
        store=store_path, shape=image.shape, chunks=(100, 100, 100), dtype=image.dtype
    )
    zarr_array[:] = image


def get_image(image_dir_path: pathlib.Path) -> np.array:
    """Read a series of jpeg to one 3D numpy array"""
    image_slices = []
    for image_slice in image_dir_path.iterdir():
        if not image_slice.is_file():
            continue

        image_slices.append(iio.imread(image_slice))

    image = np.stack(image_slices, axis=0)

    return image


def remove_output_dir(output_dir: pathlib.Path):
    if output_dir.exists():
        shutil.rmtree(output_dir)
