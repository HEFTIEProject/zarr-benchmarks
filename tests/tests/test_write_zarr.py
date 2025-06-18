from importlib.metadata import version
from importlib.util import find_spec

import numpy as np
import pytest

from zarr_benchmarks.read_write_zarr import read_write_zarr
from zarr_benchmarks.utils import is_zarr_python_v2

pytestmark = [pytest.mark.tensorstore, pytest.mark.zarr_python]


@pytest.mark.parametrize("write_empty_chunks", [True, False])
def test_write_empty_chunks_spec_3(tmp_path, write_empty_chunks):
    """Check an empty chunk is written to file when write_empty_chunks=True (zarr spec v3)"""

    if is_zarr_python_v2():
        pytest.skip("Zarr spec v3 is not supported by zarr-python v2")

    image = np.zeros(shape=(1, 1, 1))
    store_path = tmp_path / "image.zarr"

    read_write_zarr.write_zarr_array(
        image,
        store_path,
        overwrite=True,
        chunks=(1, 1, 1),
        compressor=None,
        zarr_spec=3,
        write_empty_chunks=write_empty_chunks,
    )

    assert (store_path / "zarr.json").exists()
    assert (store_path / "c" / "0" / "0" / "0").exists() == write_empty_chunks


@pytest.mark.parametrize("write_empty_chunks", [True, False])
def test_write_empty_chunks_spec_2(tmp_path, write_empty_chunks):
    """Check an empty chunk is written to file when write_empty_chunks=True (zarr spec v2)"""

    image = np.zeros(shape=(1, 1, 1))
    store_path = tmp_path / "image.zarr"

    read_write_zarr.write_zarr_array(
        image,
        store_path,
        overwrite=True,
        chunks=(1, 1, 1),
        compressor=None,
        zarr_spec=2,
        write_empty_chunks=write_empty_chunks,
    )

    assert (store_path / ".zarray").exists()
    assert (store_path / "0.0.0").exists() == write_empty_chunks


def test_read_write_zarr_import():
    """Check that the correct package is imported as read_write_zarr for each tox environment"""

    tensorstore_installed = find_spec("tensorstore") is not None
    zarr_python_installed = find_spec("zarr") is not None

    # one (and only one) of tensorstore / zarr python should be installed in each env
    assert tensorstore_installed != zarr_python_installed

    if tensorstore_installed:
        assert (
            read_write_zarr.__name__
            == "zarr_benchmarks.read_write_zarr.read_write_tensorstore"
        )
        return

    if version("zarr").split(".")[0] == "2":
        assert (
            read_write_zarr.__name__
            == "zarr_benchmarks.read_write_zarr.read_write_zarr_python_v2"
        )
        return

    if version("zarr").split(".")[0] == "3":
        assert (
            read_write_zarr.__name__
            == "zarr_benchmarks.read_write_zarr.read_write_zarr_python_v3"
        )
        return
