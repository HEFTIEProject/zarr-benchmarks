import pathlib
from typing import Literal

import numpy as np
import tensorstore as ts

from zarr_benchmarks import utils


def read_zarr_array(store_path: pathlib.Path) -> np.array:
    """Read the v2 zarr spec with tensorstore"""
    zarr_read = ts.open(
        {
            "driver": "zarr",
            "kvstore": {
                "driver": "file",
                "path": str(store_path.resolve()),
            },
        },
        read=True,
    ).result()
    read_image = zarr_read[:].read().result()
    return read_image


def write_zarr_array(
    image: np.array,
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
