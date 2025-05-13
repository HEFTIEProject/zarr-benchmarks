import pytest

import tests.tests.utils as utils

try:
    from zarr_benchmarks import read_write_zarr_v3 as read_write_zarr
except ImportError:
    read_write_zarr = pytest.importorskip("zarr_benchmarks.read_write_zarr_v2")

pytestmark = [pytest.mark.zarr_python]


@pytest.mark.parametrize("write_empty_chunks", [True, False])
def test_zarr_python_write_empty_chunks(tmp_path, write_empty_chunks):
    utils.assert_empty_chunks_written(
        tmp_path, read_write_zarr.write_zarr_array, write_empty_chunks
    )
