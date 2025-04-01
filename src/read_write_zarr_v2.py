import zarr
import numcodecs
from numcodecs import Blosc, GZip, Zstd
import pathlib
import utils
import numpy as np


def get_compression_ratio(store_path: pathlib.Path) -> float:
    zarr_array = zarr.open_array(store_path, mode="r")
    compression_ratio = zarr_array.nbytes / zarr_array.nbytes_stored

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
    compressor: numcodecs.abc.Codec,
) -> None:
    if overwrite:
        utils.remove_output_dir(store_path)

    zarr_array = zarr.open_array(
        store=store_path,
        mode="w-",
        shape=image.shape,
        chunks=chunks,
        dtype=image.dtype,
        compressor=compressor,
    )
    zarr_array[:] = image


def get_blosc_compressor(cname: str, clevel: int, shuffle: str) -> numcodecs.abc.Codec:
    shuffle_int = utils.get_numcodec_shuffle(shuffle)
    return Blosc(cname=cname, clevel=clevel, shuffle=shuffle_int)


def get_gzip_compressor(level: int) -> numcodecs.abc.Codec:
    return GZip(level=level)


def get_zstd_compressor(level: int) -> numcodecs.abc.Codec:
    return Zstd(level=level)
