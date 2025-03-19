import pytest
import pathlib
from src.read_write_zarr import get_image
import numpy as np


@pytest.fixture(scope="session")
def image():
    """Reading the image from jpeg is slow, so we only do it once per testing session."""
    image = get_image(
        image_dir_path=pathlib.Path(
            "data/input/_200.64um_LADAF-2021-17_heart_complete-organ_pag-0.10_0.03_jp2_"
        )
    )
    # image = np.random.rand(100, 100, 100)

    return image
