import numpy as np
import pathlib
import tensorstore as ts
from utils import remove_output_dir


def read_zarr_array(store_path: pathlib.Path) -> np.array:
    zarr_read = ts.open(
        {
            "driver": "zarr",
            "kvstore": {
                "driver": "file",
                "path": store_path,
            },
        },
        read=True,
    ).result()
    read_image = zarr_read[:].read().result()
    return read_image


def write_zarr_array(
    image: np.array,
    store_path: pathlib.Path,
    overwrite: bool,
    chunks: tuple[int],
    compressor: dict,
) -> None:
    if overwrite:
        remove_output_dir(store_path)

    dataset = ts.open(
        {
            "driver": "zarr",
            "kvstore": {
                "driver": "file",
                "path": store_path,
            },
            "metadata": {
                "dtype": image.dtype.str,
                "shape": image.shape,
                "chunks": chunks,
                "compressor": compressor,
            },
            "create": True,
            "delete_existing": False,
        },
    ).result()

    write_future = dataset[:].write(image)
    write_future.result()


def get_blosc_compressor(cname: str, clevel: int, shuffle: str) -> dict:
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
