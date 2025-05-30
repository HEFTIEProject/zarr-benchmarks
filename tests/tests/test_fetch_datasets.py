import pytest

from zarr_benchmarks import fetch_datasets

pytestmark = [pytest.mark.tensorstore, pytest.mark.zarr_python]


def test_heart_image():
    """Check heart image is correctly fetched / cached from zenodo."""

    image = fetch_datasets.get_image()
    assert image.shape == (806, 629, 629)
