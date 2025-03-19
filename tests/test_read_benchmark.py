import pytest
from src.read_write_zarr import write_zarr_array, read_zarr_array, get_compression_ratio
import pathlib
import numpy as np


@pytest.mark.benchmark(
    group="group-name",
)
def test_read(benchmark):
    # image = get_image(image_dir_path=pathlib.Path('data/input/_200.64um_LADAF-2021-17_heart_complete-organ_pag-0.10_0.03_jp2_'))
    image = np.random.rand(100, 100, 100)
    store_path = pathlib.Path("data/output/heart-example.zarr")
    overwrite = True
    write_zarr_array(image, store_path, overwrite)
    compression_ratio = get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(read_zarr_array, args=(store_path,), rounds=3, warmup_rounds=1)
