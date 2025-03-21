import pytest
import pathlib
from utils import get_image


@pytest.fixture(scope="session")
def image():
    """Reading the image from jpeg is slow, so we only do it once per testing session."""
    image = get_image(
        image_dir_path=pathlib.Path(
            "data/input/_200.64um_LADAF-2021-17_heart_complete-organ_pag-0.10_0.03_jp2_"
        )
    )

    return image


@pytest.fixture()
def store_path():
    """Path to store zarr images written from benchmarks"""
    return pathlib.Path("data/output/heart-example.zarr")
