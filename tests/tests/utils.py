from pathlib import Path
from typing import Callable

import numpy as np


def assert_empty_chunks_written(
    output_dir: Path, write_zarr_array: Callable, write_empty_chunks: bool
) -> None:
    """Check an empty chunk is written to file when write_empty_chunks=True"""

    image = np.zeros(shape=(1, 1, 1))
    store_path = output_dir / "image.zarr"

    write_zarr_array(
        image,
        store_path,
        overwrite=True,
        chunks=(1, 1, 1),
        compressor=None,
        write_empty_chunks=write_empty_chunks,
    )

    assert (store_path / ".zarray").exists()
    assert (store_path / "0.0.0").exists() == write_empty_chunks
