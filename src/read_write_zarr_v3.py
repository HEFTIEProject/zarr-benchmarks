import pathlib
import numpy as np
import zarr
from numcodecs import Blosc, GZip, Zstd
from zarr.codecs import BloscCodec, GzipCodec, ZstdCodec
from typing import Any
import utils


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
    zarr_spec: int = 2,
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
    )
    zarr_array[:] = image


def get_blosc_compressor(
    cname: str, clevel: int, shuffle: str, zarr_spec: int = 2
) -> Any:
    if zarr_spec == 2:
        shuffle_int = utils.get_numcodec_shuffle(shuffle)
        return Blosc(cname=cname, clevel=clevel, shuffle=shuffle_int)
    elif zarr_spec == 3:
        return BloscCodec(cname=cname, clevel=clevel, shuffle=shuffle)
    else:
        raise ValueError(f"invalid zarr spec version {zarr_spec}")


def get_gzip_compressor(level: int, zarr_spec: int = 2) -> Any:
    if zarr_spec == 2:
        return GZip(level=level)
    elif zarr_spec == 3:
        return GzipCodec(level=level)
    else:
        raise ValueError(f"invalid zarr spec version {zarr_spec}")


def get_zstd_compressor(level: int, zarr_spec: int = 2) -> Any:
    if zarr_spec == 2:
        return Zstd(level=level)
    elif zarr_spec == 3:
        return ZstdCodec(level=level)
    else:
        raise ValueError(f"invalid zarr spec version {zarr_spec}")
