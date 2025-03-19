import pytest
from src.read_write_zarr import write_zarr_array, remove_output_dir
import pathlib


@pytest.mark.benchmark(
    group="group-name",
)
def test_write(benchmark, image):
    store_path = pathlib.Path("data/output/heart-example.zarr")
    overwrite = True

    def setup():
        return (image, store_path, overwrite), {}

    benchmark.pedantic(write_zarr_array, setup=setup, rounds=3, warmup_rounds=1)


@pytest.mark.benchmark(
    group="group-name",
)
def test_write_without_removal(benchmark, image):
    store_path = pathlib.Path("data/output/heart-example.zarr")
    overwrite = False

    def setup():
        remove_output_dir(store_path)
        return (image, store_path, overwrite), {}

    benchmark.pedantic(write_zarr_array, setup=setup, rounds=3, warmup_rounds=1)
