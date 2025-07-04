import json
import os
import pathlib
import shutil
from importlib.metadata import version
from importlib.util import find_spec


def is_zarr_python_v2() -> bool:
    """
    Check if the zarr-python version is v2.
    """
    if find_spec("zarr") and version("zarr").split(".")[0] == "2":
        return True

    return False


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
