import zarr
import read_write_zarr_v2
import read_write_zarr_v3
from typing import Any
from collections.abc import Callable
import pathlib


def get_zarr_read_function() -> Callable:
    if zarr.__version__[0] == "2":
        return read_write_zarr_v2.read_zarr_array
    else:
        return read_write_zarr_v3.read_zarr_array


def get_zarr_write_function() -> Callable:
    if zarr.__version__[0] == "2":
        return read_write_zarr_v2.write_zarr_array
    else:
        return read_write_zarr_v3.write_zarr_array


def get_blosc_compressor(cname: str, clevel: int, shuffle: str) -> Any:
    if zarr.__version__[0] == "2":
        return read_write_zarr_v2.get_blosc_compressor(cname, clevel, shuffle)
    else:
        return read_write_zarr_v3.get_blosc_compressor(cname, clevel, shuffle)


def get_gzip_compressor(level: int) -> Any:
    if zarr.__version__[0] == "2":
        return read_write_zarr_v2.get_gzip_compressor(level)
    else:
        return read_write_zarr_v3.get_gzip_compressor(level)


def get_zstd_compressor(level: int) -> Any:
    if zarr.__version__[0] == "2":
        return read_write_zarr_v2.get_zstd_compressor(level)
    else:
        return read_write_zarr_v3.get_zstd_compressor(level)


def get_compression_ratio(store_path: pathlib.Path) -> float:
    if zarr.__version__[0] == "2":
        return read_write_zarr_v2.get_compression_ratio(store_path)
    else:
        return read_write_zarr_v3.get_compression_ratio(store_path)
