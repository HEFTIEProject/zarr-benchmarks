import itertools
import pathlib

import numpy as np
import pytest

from zarr_benchmarks.utils import get_image, read_json_file


def pytest_addoption(parser):
    parser.addoption(
        "--config",
        action="store",
        default="dev",
        type=str,
        help="Name of config json file from tests/benchmarks/benchmark_configs, or 'all' to combine all configs (excluding the 'dev' config)",
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
