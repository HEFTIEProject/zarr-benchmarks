import pathlib
from typing import Literal

import numpy.typing as npt
import tensorstore as ts

from zarr_benchmarks import utils


def get_compression_ratio(store_path: pathlib.Path, zarr_spec: Literal[2, 3]) -> float:
    zarr_array = open_zarr_array(store_path, zarr_spec)
    item_size = zarr_array.dtype.numpy_dtype.itemsize
    nbytes = item_size * zarr_array.size
    nbytes_stored = utils.get_directory_size(store_path)
    return nbytes / nbytes_stored


def open_zarr_array(
    store_path: pathlib.Path, zarr_spec: Literal[2, 3]
) -> ts.TensorStore:
    if zarr_spec == 2:
        driver = "zarr"
    else:
        driver = "zarr3"

    return ts.open(
        {
            "driver": driver,
            "kvstore": {
                "driver": "file",
                "path": str(store_path.resolve()),
            },
        },
    ).result()


def read_zarr_array(store_path: pathlib.Path, zarr_spec: Literal[2, 3]) -> npt.NDArray:
    """Read the v2/v3 zarr spec with tensorstore"""
    zarr_read = open_zarr_array(store_path, zarr_spec)
    read_image = zarr_read[:].read().result()
    return read_image


def write_zarr_array_v2(
    image: npt.NDArray,
    store_path: pathlib.Path,
    *,
    chunks: tuple[int],
    compressor: dict | None,
    write_empty_chunks: bool = True,
) -> None:
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


def write_zarr_array_v3(
    image: npt.NDArray,
    store_path: pathlib.Path,
    *,
    chunks: tuple[int],
    compressor: dict | None,
    write_empty_chunks: bool = True,
) -> None:
    dataset = ts.open(
        {
            "driver": "zarr3",
            "kvstore": {
                "driver": "file",
                "path": str(store_path.resolve()),
            },
            "metadata": {
                "zarr_format": 3,
                "node_type": "array",
                "data_type": str(image.dtype),
                "shape": image.shape,
                "chunk_grid": {
                    "name": "regular",
                    "configuration": {"chunk_shape": chunks},
                },
                "codecs": (
                    [
                        {"name": "bytes", "configuration": {"endian": "little"}},
                        compressor,
                    ]
                    if compressor is not None
                    else [{"name": "bytes", "configuration": {"endian": "little"}}]
                ),
                "fill_value": 0,
            },
            "create": True,
            "delete_existing": False,
            "store_data_equal_to_fill_value": write_empty_chunks,
        },
    ).result()

    write_future = dataset[:].write(image)
    write_future.result()


def write_zarr_array(
    image: npt.NDArray,
    store_path: pathlib.Path,
    *,
    overwrite: bool,
    chunks: tuple[int],
    compressor: dict | None,
    write_empty_chunks: bool = True,
    zarr_spec: Literal[2, 3] = 2,
) -> None:
    """Write the v2/v3 zarr spec with tensorstore"""
    if overwrite:
        utils.remove_output_dir(store_path)

    if zarr_spec == 2:
        write_zarr_array_v2(
            image,
            store_path,
            chunks=chunks,
            compressor=compressor,
            write_empty_chunks=write_empty_chunks,
        )
    else:
        write_zarr_array_v3(
            image,
            store_path,
            chunks=chunks,
            compressor=compressor,
            write_empty_chunks=write_empty_chunks,
        )


def get_blosc_compressor(
    cname: str,
    clevel: int,
    shuffle: Literal["shuffle", "noshuffle", "bitshuffle"],
    zarr_spec: Literal[2, 3],
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

    if zarr_spec == 2:
        return {"id": "blosc", "cname": cname, "clevel": clevel, "shuffle": shuffle_int}
    else:
        return {
            "name": "blosc",
            "configuration": {"cname": cname, "clevel": clevel, "shuffle": shuffle},
        }


def get_gzip_compressor(level: int, zarr_spec: Literal[2, 3]) -> dict:
    if zarr_spec == 2:
        return {"id": "gzip", "level": level}
    else:
        return {"name": "gzip", "configuration": {"level": level}}


def get_zstd_compressor(level: int, zarr_spec: Literal[2, 3]) -> dict:
    if zarr_spec == 2:
        return {"id": "zstd", "level": level}
    else:
        return {"name": "zstd", "configuration": {"level": level}}
