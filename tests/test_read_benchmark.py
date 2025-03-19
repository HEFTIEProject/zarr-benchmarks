import pytest
from src.read_write_zarr import write_zarr_array, read_zarr_array, get_compression_ratio
from tests.benchmark_parameters import CHUNK_SIZE, COMPRESSORS
import pathlib


@pytest.mark.benchmark(
    group="read",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize(
    "compressors", COMPRESSORS, ids=[type(compressor) for compressor in COMPRESSORS]
)
def test_read(benchmark, image, chunk_size, compressors):
    store_path = pathlib.Path("data/output/heart-example.zarr")
    overwrite = True
    chunks = (chunk_size, chunk_size, chunk_size)
    write_zarr_array(image, store_path, overwrite, chunks, compressors)

    compression_ratio = get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(read_zarr_array, args=(store_path,), rounds=3, warmup_rounds=1)
