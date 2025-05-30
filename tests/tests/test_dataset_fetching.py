import pytest

from zarr_benchmarks import utils

pytestmark = [pytest.mark.tensorstore, pytest.mark.zarr_python]


def test_heart_image():
    """Check heart image is correctly fetched / cached from zenodo."""

    image = utils.get_image()
    assert image.shape == (806, 629, 629)
