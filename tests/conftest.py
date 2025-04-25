import json
import pathlib

import numpy as np
import pytest

from zarr_benchmarks.utils import get_image


def pytest_addoption(parser):
    parser.addoption(
        "--config",
        action="store",
        default="tests/benchmarks/benchmark_configs/default.json",
        type=str,
        help="path to benchmark config json file",
    )

    parser.addoption(
        "--dev-image",
        action="store_true",
        help="Use a small 100x100x100 image to test benchmarks",
    )

    parser.addoption(
        "--rounds",
        action="store",
        default=3,
        type=int,
        help="number of rounds for each benchmark",
    )

    parser.addoption(
        "--warmup-rounds",
        action="store",
        default=1,
        type=int,
        help="number of warmup rounds for each benchmark",
    )


@pytest.fixture
def rounds(request):
    return request.config.getoption("--rounds")


@pytest.fixture
def warmup_rounds(request):
    return request.config.getoption("--warmup-rounds")


@pytest.fixture(scope="session")
def dev_image(request):
    return request.config.getoption("--dev-image")


@pytest.fixture(scope="session")
def image(dev_image):
    """If '--dev_image' isn't set, read the image from a series of jpeg. This process is quite slow, so we only do it once
    per testing session. If '--dev_image' is set, use a small 100x100x100 numpy array instead - this is useful for quick
    test runs during development."""

    if dev_image:
        return np.random.rand(100, 100, 100)

    return get_image(
        image_dir_path=pathlib.Path(
            "data/input/_200.64um_LADAF-2021-17_heart_complete-organ_pag-0.10_0.03_jp2_"
        )
    )


@pytest.fixture()
def store_path():
    """Path to store zarr images written from benchmarks"""
    return pathlib.Path("data/output/heart-example.zarr")


def pytest_generate_tests(metafunc):
    """Parse the config file, and pass the read parameters to the relevant fixtures"""

    config_path = metafunc.config.getoption("config")
    with open(config_path) as f:
        config = json.load(f)

    for key, values in config.items():
        if key in metafunc.fixturenames:
            metafunc.parametrize(key, values)
