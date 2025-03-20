import pytest
from src.read_write_zarr import write_zarr_array, remove_output_dir
import pathlib
from tests.benchmark_parameters import CHUNK_SIZE, COMPRESSORS


@pytest.mark.benchmark(
    group="write",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize(
    "compressors", COMPRESSORS, ids=[type(compressor) for compressor in COMPRESSORS]
)
def test_write(benchmark, image, chunk_size, compressors):
    store_path = pathlib.Path("data/output/heart-example.zarr")
    overwrite = False

    def setup():
        remove_output_dir(store_path)
        return (
            image,
            store_path,
            overwrite,
            (chunk_size, chunk_size, chunk_size),
            compressors,
        ), {}

    benchmark.pedantic(write_zarr_array, setup=setup, rounds=3, warmup_rounds=1)
