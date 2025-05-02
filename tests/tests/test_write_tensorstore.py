import pytest

import tests.tests.utils as utils

read_write_tensorstore = pytest.importorskip("zarr_benchmarks.read_write_tensorstore")
pytestmark = [pytest.mark.tensorstore]


@pytest.mark.parametrize("write_empty_chunks", [True, False])
def test_tensorstore_write_empty_chunks(tmp_path, write_empty_chunks):
    utils.assert_empty_chunks_written(
        tmp_path, read_write_tensorstore.write_zarr_array, write_empty_chunks
    )
