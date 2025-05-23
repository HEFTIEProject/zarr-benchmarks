import pathlib
from typing import Literal

import numpy.typing as npt
import tensorstore as ts

from zarr_benchmarks import utils


def get_compression_ratio(store_path: pathlib.Path) -> float:
    zarr_array = open_zarr_array(store_path)
    item_size = zarr_array.dtype.numpy_dtype.itemsize
    nbytes = item_size * zarr_array.size
    nbytes_stored = utils.get_directory_size(store_path)
    return nbytes / nbytes_stored


def open_zarr_array(store_path: pathlib.Path) -> ts.TensorStore:
    return ts.open(
        {
            "driver": "zarr",
            "kvstore": {
                "driver": "file",
                "path": str(store_path.resolve()),
            },
        },
    ).result()


def read_zarr_array(store_path: pathlib.Path) -> npt.NDArray:
    """Read the v2 zarr spec with tensorstore"""
    zarr_read = open_zarr_array(store_path)
    read_image = zarr_read[:].read().result()
    return read_image


def write_zarr_array(
    image: npt.NDArray,
    store_path: pathlib.Path,
    *,
    overwrite: bool,
    chunks: tuple[int],
    compressor: dict,
    write_empty_chunks: bool = True,
) -> None:
    """Write the v2 zarr spec with tensorstore"""
    if overwrite:
        utils.remove_output_dir(store_path)

    dataset = ts.open(
        {
            "driver": "zarr",
            "kvstore": {
                "driver": "file",
                "path": str(store_path.resolve()),
            },
            "metadata": {
                "dtype": image.dtype.str,
                "shape": image.shape,
                "chunks": chunks,
                "compressor": compressor,
                "fill_value": 0,
            },
            "create": True,
            "delete_existing": False,
            "store_data_equal_to_fill_value": write_empty_chunks,
        },
    ).result()

    write_future = dataset[:].write(image)
    write_future.result()


def get_blosc_compressor(
    cname: str, clevel: int, shuffle: Literal["shuffle", "noshuffle", "bitshuffle"]
) -> dict:
    # see the zarr shuffle docs: https://google.github.io/tensorstore/driver/zarr/index.html#json-driver/zarr/Compressor/blosc.shuffle
    match shuffle:
        case "noshuffle":
            shuffle_int = 0
        case "shuffle":
            shuffle_int = 1
        case "bitshuffle":
            shuffle_int = 2
        case _:
            raise ValueError(f"invalid shuffle value for blosc {shuffle}")

    return {"id": "blosc", "cname": cname, "clevel": clevel, "shuffle": shuffle_int}


def get_gzip_compressor(level: int) -> dict:
    return {"id": "gzip", "level": level}


def get_zstd_compressor(level: int) -> dict:
    return {"id": "zstd", "level": level}
