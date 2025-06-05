import pathlib
from typing import Any, Literal

import numpy.typing as npt
import zarr
from numcodecs import Blosc, GZip, Zstd
from zarr.codecs import BloscCodec, GzipCodec, ZstdCodec

from zarr_benchmarks import utils
from zarr_benchmarks.read_write_zarr import read_write_zarr_python_utils


def get_compression_ratio(store_path: pathlib.Path) -> float:
    zarr_array = zarr.open_array(store_path, mode="r")
    compression_ratio = zarr_array.nbytes / zarr_array.nbytes_stored()

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
    compressor: Any = "auto",
    zarr_spec: Literal[2, 3] = 2,
    write_empty_chunks: bool = True,
) -> None:
    if overwrite:
        utils.remove_output_dir(store_path)

    zarr_array = zarr.create_array(
        store=store_path,
        shape=image.shape,
        chunks=chunks,
        dtype=image.dtype,
        compressors=compressor,
        zarr_format=zarr_spec,
        fill_value=0,
        config={"write_empty_chunks": write_empty_chunks},
    )
    zarr_array[:] = image


def get_blosc_compressor(
    cname: str,
    clevel: int,
    shuffle: Literal["shuffle", "noshuffle", "bitshuffle"],
    zarr_spec: Literal[2, 3] = 2,
) -> Any:
    if zarr_spec == 2:
        shuffle_int = read_write_zarr_python_utils.get_numcodec_shuffle(shuffle)
        return Blosc(cname=cname, clevel=clevel, shuffle=shuffle_int)
    elif zarr_spec == 3:
        return BloscCodec(cname=cname, clevel=clevel, shuffle=shuffle)
    else:
        raise ValueError(f"invalid zarr spec version {zarr_spec}")


def get_gzip_compressor(level: int, zarr_spec: Literal[2, 3] = 2) -> Any:
    if zarr_spec == 2:
        return GZip(level=level)
    elif zarr_spec == 3:
        return GzipCodec(level=level)
    else:
        raise ValueError(f"invalid zarr spec version {zarr_spec}")


def get_zstd_compressor(level: int, zarr_spec: Literal[2, 3] = 2) -> Any:
    if zarr_spec == 2:
        return Zstd(level=level)
    elif zarr_spec == 3:
        return ZstdCodec(level=level)
    else:
        raise ValueError(f"invalid zarr spec version {zarr_spec}")
