import pathlib
import numpy as np
import zarr
import zarr.codecs
from typing import Any
from src.utils import remove_output_dir


def get_compression_ratio(store_path: pathlib.Path) -> float:
    zarr_array = zarr.open_array(store_path, mode="r")
    compression_ratio = zarr_array.nbytes / zarr_array.nbytes_stored()

    return compression_ratio


def read_zarr_array(store_path: pathlib.Path) -> np.array:
    zarr_read = zarr.open_array(store_path, mode="r")
    read_image = zarr_read[:]
    return read_image


def write_zarr_array(
    image: np.array,
    store_path: pathlib.Path,
    overwrite: bool,
    chunks: tuple[int],
    compressor: Any = "auto",
) -> None:
    if overwrite:
        remove_output_dir(store_path)

    zarr_array = zarr.create_array(
        store=store_path,
        shape=image.shape,
        chunks=chunks,
        dtype=image.dtype,
        compressors=compressor,
    )
    zarr_array[:] = image


def get_blosc_compressor(cname: str, clevel: int, shuffle: str) -> Any:
    return zarr.codecs.BloscCodec(cname=cname, clevel=clevel, shuffle=shuffle)
