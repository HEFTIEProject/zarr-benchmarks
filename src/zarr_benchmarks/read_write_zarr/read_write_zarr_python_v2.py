import pathlib
from typing import Literal

import numcodecs
import numpy.typing as npt
import zarr
from numcodecs import Blosc, GZip, Zstd

from zarr_benchmarks import utils
from zarr_benchmarks.read_write_zarr import read_write_zarr_python_utils


def get_compression_ratio(store_path: pathlib.Path) -> float:
    zarr_array = zarr.open_array(store_path, mode="r")
    compression_ratio = zarr_array.nbytes / zarr_array.nbytes_stored

    return compression_ratio


def read_zarr_array(store_path: pathlib.Path) -> npt.NDArray:
    zarr_read = zarr.open_array(store_path, mode="r")
    read_image = zarr_read[:]
    return read_image


def write_zarr_array(
    image: npt.NDArray,
    store_path: pathlib.Path,
    *,
    overwrite: bool,
    chunks: tuple[int],
    compressor: numcodecs.abc.Codec | None,
    write_empty_chunks: bool = True,
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
        fill_value=0,
        write_empty_chunks=write_empty_chunks,
    )
    zarr_array[:] = image


def get_blosc_compressor(
    cname: str, clevel: int, shuffle: Literal["shuffle", "noshuffle", "bitshuffle"]
) -> numcodecs.abc.Codec:
    shuffle_int = read_write_zarr_python_utils.get_numcodec_shuffle(shuffle)
    return Blosc(cname=cname, clevel=clevel, shuffle=shuffle_int)


def get_gzip_compressor(level: int) -> numcodecs.abc.Codec:
    return GZip(level=level)


def get_zstd_compressor(level: int) -> numcodecs.abc.Codec:
    return Zstd(level=level)
