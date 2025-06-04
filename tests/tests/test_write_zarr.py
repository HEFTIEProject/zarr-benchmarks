import numpy as np
import pytest

from zarr_benchmarks.read_write_zarr import read_write_zarr

pytestmark = [pytest.mark.tensorstore, pytest.mark.zarr_python]


@pytest.mark.parametrize("write_empty_chunks", [True, False])
def test_write_empty_chunks(tmp_path, write_empty_chunks):
    """Check an empty chunk is written to file when write_empty_chunks=True"""

    image = np.zeros(shape=(1, 1, 1))
    store_path = tmp_path / "image.zarr"

    read_write_zarr.write_zarr_array(
        image,
        store_path,
        overwrite=True,
        chunks=(1, 1, 1),
        compressor=None,
        write_empty_chunks=write_empty_chunks,
    )

    assert (store_path / ".zarray").exists()
    assert (store_path / "0.0.0").exists() == write_empty_chunks
