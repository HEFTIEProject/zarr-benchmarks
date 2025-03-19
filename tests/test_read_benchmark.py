import pytest
from src.read_write_zarr import write_zarr_array, read_zarr_array, get_compression_ratio
import pathlib


@pytest.mark.benchmark(
    group="group-name",
)
def test_read(benchmark, image):
    store_path = pathlib.Path("data/output/heart-example.zarr")
    overwrite = True
    write_zarr_array(image, store_path, overwrite)
    compression_ratio = get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(read_zarr_array, args=(store_path,), rounds=3, warmup_rounds=1)
