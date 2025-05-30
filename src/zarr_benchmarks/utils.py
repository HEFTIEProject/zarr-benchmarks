import json
import os
import pathlib
import shutil

import numpy.typing as npt
import pooch

try:
    from zarr_benchmarks import read_write_zarr_v3 as read_write_zarr
except ImportError:
    try:
        from zarr_benchmarks import (  # type: ignore[no-redef]
            read_write_zarr_v2 as read_write_zarr,
        )
    except ImportError:
        from zarr_benchmarks import (  # type: ignore[no-redef]
            read_write_tensorstore as read_write_zarr,
        )

ZENODO = pooch.create(
    # Use the default cache folder for the operating system
    path=pooch.os_cache("zarr-benchmarks"),
    base_url="doi:10.5281/zenodo.15544055",
    registry=None,
)
ZENODO.load_registry_from_doi()


def get_image() -> npt.NDArray:
    """Fetch zarr image from zenodo (if not already cached), and return as a 3D numpy array"""

    heart_image = "200.64um_LADAF-2021-17_heart_complete-organ_pag.zarr"
    unpack = pooch.Unzip(members=[heart_image])
    ZENODO.fetch(f"{heart_image}.zip", processor=unpack)
    heart_image_path = ZENODO.path / f"{heart_image}.zip.unzip" / heart_image

    # open zarr
    image = read_write_zarr.read_zarr_array(heart_image_path)

    return image


def remove_output_dir(output_dir: pathlib.Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)


def get_directory_size(path: pathlib.Path) -> int:
    """
    Get total size of a directory in bytes.
    """
    total_size = 0
    if not path.is_dir():
        raise ValueError(f"Path not a directory: {path}")
    for dirpath, dirnames, filenames in path.walk():
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    return total_size


def read_json_file(path_to_file: pathlib.Path) -> dict:
    with open(path_to_file, "r") as f:
        return json.load(f)
