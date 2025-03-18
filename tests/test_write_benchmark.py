import pytest
from src.read_write_zarr import get_image, write_zarr_array, remove_output_dir
import pathlib
import numpy as np

@pytest.mark.benchmark(
    group="group-name",
)
def test_write(benchmark):
    # image = get_image(image_dir_path=pathlib.Path('data/input/_200.64um_LADAF-2021-17_heart_complete-organ_pag-0.10_0.03_jp2_'))
    image = np.random.rand(4, 4, 4)
    store_path=pathlib.Path('data/output/heart-example.zarr')
    overwrite=True
    def setup():
        return (image, store_path, overwrite), {}
    
    benchmark.pedantic(write_zarr_array, setup=setup, rounds=3, warmup_rounds=1)
    
    
@pytest.mark.benchmark(
    group="group-name",
)
def test_write_without_removal(benchmark):
    # image = get_image(image_dir_path=pathlib.Path('data/input/_200.64um_LADAF-2021-17_heart_complete-organ_pag-0.10_0.03_jp2_'))
    image = np.random.rand(4, 4, 4)
    store_path=pathlib.Path('data/output/heart-example.zarr')
    overwrite=False
    def setup():
        remove_output_dir(store_path)
        return (image, store_path, overwrite), {}
    
    benchmark.pedantic(write_zarr_array, setup=setup, rounds=3, warmup_rounds=1)
