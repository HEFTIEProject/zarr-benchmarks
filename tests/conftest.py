import itertools
import pathlib

import numpy as np
import pytest

from zarr_benchmarks.fetch_datasets import (
    get_dense_segmentation,
    get_heart,
    get_sparse_segmentation,
)
from zarr_benchmarks.utils import read_json_file


def pytest_addoption(parser):
    parser.addoption(
        "--config",
        action="store",
        default="dev",
        type=str,
        help="Name of config json file from tests/benchmarks/benchmark_configs, or 'all' to combine all configs (excluding the 'dev' config)",
    )

    parser.addoption(
        "--image",
        action="store",
        default="dev",
        type=str,
        choices=["dev", "heart", "dense", "sparse"],
        help="Type of image to run benchmarks with: 'dev' is a small 128x128x128 numpy array for testing purposes, "
        "'heart' is an image of a heart from the human organ atlas, 'dense' is a dense segmentation (small subset of "
        "C3 segmentation data from the H01 release) and 'sparse' is a sparse segmentation (small subset of '104 "
        "proofread cells' from the H01 release).",
    )

    parser.addoption(
        "--rounds",
        action="store",
        default=5,
        type=int,
        help="Number of rounds for each benchmark",
    )

    parser.addoption(
        "--warmup-rounds",
        action="store",
        default=1,
        type=int,
        help="Number of warmup rounds for each benchmark",
    )


@pytest.fixture
def rounds(request):
    return request.config.getoption("--rounds")


@pytest.fixture
def warmup_rounds(request):
    return request.config.getoption("--warmup-rounds")


@pytest.fixture(scope="session")
def image(request):
    """Return image selected via --image option as a numpy array. If --image=dev, a small 128x128x128 numpy array is
    used, otherwise the relevant image is fetched from zenodo (or the cache if already downloaded). Reading the full
    size images are quite slow, so we only do it once per testing session."""

    image_type = request.config.getoption("--image")

    match image_type:
        case "dev":
            return np.random.rand(128, 128, 128)
        case "heart":
            return get_heart()
        case "dense":
            return get_dense_segmentation()
        case "sparse":
            return get_sparse_segmentation()
        case _:
            raise ValueError(f"Invalid --image option {image_type}")


@pytest.fixture()
def store_path():
    """Path to store zarr images written from benchmarks"""
    return pathlib.Path("data/output/temp-benchmarks.zarr")


def _expand_min_max(config: dict) -> dict:
    """Expand min/max keys in config to a list of the full range of values."""

    for key in ["chunk_size", "blosc_clevel", "gzip_level", "zstd_level"]:
        values = config[key]
        if "min" in values and "max" in values:
            config[key] = range(values["min"], values["max"] + 1)

    return config


def _parse_config_file(config_path: pathlib.Path) -> dict:
    config = _expand_min_max(read_json_file(config_path))

    # make bool 'no_compressor' a list, to match the other parameters (allows itertools.product to work)
    config["no_compressor"] = [config["no_compressor"]]

    return config


def _parse_config_files(config_name: str) -> list[dict]:
    """Parse json config files. 'all' will parse every config in tests/benchmark_configs (except for dev, which contains
    a small set of parameters for development runs)."""

    configs_dir = pathlib.Path(__file__).parent / "benchmarks" / "benchmark_configs"
    configs = []

    if config_name == "all":
        for config_file in configs_dir.glob("*.json"):
            if config_file.stem != "dev":
                config = _parse_config_file(config_file)
                configs.append(config)
    else:
        config_file = configs_dir / f"{config_name}.json"
        config = _parse_config_file(config_file)
        configs.append(config)

    return configs


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parse the config file, and parametrize the given function with these values. pytest_generate_tests is called
    once per test function, during the collection stage."""

    config_name = metafunc.config.getoption("config")
    configs = _parse_config_files(config_name)

    # keys from the config, that are used as arguments for this function
    used_config_keys = [key for key in configs[0] if key in metafunc.fixturenames]
    if len(used_config_keys) == 0:
        return

    # generate all combinations of parameters for each config, and add to a set to remove any duplicate combos
    parametrize_values: set[tuple] = set()
    for config in configs:
        parameter_values = [config[key] for key in used_config_keys]
        parameter_combinations = tuple(itertools.product(*parameter_values))
        parametrize_values.update(parameter_combinations)

    # sort values for parametrize, so they are more readable in pytest output
    parametrize_values_list = sorted(list(parametrize_values))

    metafunc.parametrize(used_config_keys, parametrize_values_list)
