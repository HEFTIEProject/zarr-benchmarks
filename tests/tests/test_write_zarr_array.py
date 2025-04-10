import numpy as np
import pytest
import read_write_tensorstore
from pathlib import Path

try:
    import read_write_zarr_v3 as read_write_zarr
except ImportError:
    import read_write_zarr_v2 as read_write_zarr


def assert_empty_chunks_written(
    output_dir: Path, write_zarr_array: callable, write_empty_chunks: bool
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


@pytest.mark.zarr_python
@pytest.mark.parametrize("write_empty_chunks", [True, False])
def test_zarr_python_write_empty_chunks(tmp_path, write_empty_chunks):
    assert_empty_chunks_written(
        tmp_path, read_write_zarr.write_zarr_array, write_empty_chunks
    )


@pytest.mark.tensorstore
@pytest.mark.parametrize("write_empty_chunks", [True, False])
def test_tensorstore_write_empty_chunks(tmp_path, write_empty_chunks):
    assert_empty_chunks_written(
        tmp_path, read_write_tensorstore.write_zarr_array, write_empty_chunks
    )
