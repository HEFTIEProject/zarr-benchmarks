import pytest
from pytest_lazyfixture import lazy_fixture

from tests.benchmarks.benchmark_parameters import (
    CHUNK_SIZE,
    ZSTD_LEVEL,
)
from tests.benchmarks.benchmark_parameters_mult_runs import parameters

try:
    import read_write_zarr_v3 as read_write_zarr
except ImportError:
    import read_write_zarr_v2 as read_write_zarr

pytestmark = [pytest.mark.zarr_python]

plot_run_1_params = parameters["plot_run_1"]
plot_run_2_params = parameters["plot_run_2"]
plot_run_3_params = parameters["plot_run_3"]


@pytest.fixture
def plot_run_1_params_fix():
    return {
        "CHUNK_SIZE": plot_run_1_params["CHUNK_SIZE"],
        "BLOSC_CLEVEL": plot_run_1_params["BLOSC_CLEVEL"],
        "BLOSC_SHUFFLE": plot_run_1_params["BLOSC_SHUFFLE"],
        "BLOSC_CNAME": plot_run_1_params["BLOSC_CNAME"],
    }


@pytest.fixture
def plot_run_2_params_fix():
    return {
        "CHUNK_SIZE": [60, 61, 62],
        "BLOSC_CLEVEL": [4, 5, 6],
        "BLOSC_SHUFFLE": "shuffle",
        "BLOSC_CNAME": "zstd",
    }


@pytest.fixture
def plot_run_3_params_fix():
    return {
        "CHUNK_SIZE": [60, 61, 62],
        "BLOSC_CLEVEL": [4, 5, 6],
        "BLOSC_SHUFFLE": ["shuffle"],
        "BLOSC_CNAME": "zstd",
    }


@pytest.mark.benchmark(group="read")
@pytest.mark.parametrize(
    "chunk_size",
    [
        lazy_fixture("plot_run_1_params_fix"),
        lazy_fixture("plot_run_2_params_fix"),
        lazy_fixture("plot_run_3_params_fix"),
    ],
)
@pytest.mark.parametrize(
    "blosc_clevel",
    [
        lazy_fixture("plot_run_1_params_fix"),
        lazy_fixture("plot_run_2_params_fix"),
        lazy_fixture("plot_run_3_params_fix"),
    ],
)
@pytest.mark.parametrize(
    "blosc_shuffle",
    [
        lazy_fixture("plot_run_1_params_fix"),
        lazy_fixture("plot_run_2_params_fix"),
        lazy_fixture("plot_run_3_params_fix"),
    ],
)
@pytest.mark.parametrize(
    "blosc_cname",
    [
        lazy_fixture("plot_run_1_params_fix"),
        lazy_fixture("plot_run_2_params_fix"),
        lazy_fixture("plot_run_3_params_fix"),
    ],
)
def test_read_blosc(
    benchmark,
    image,
    rounds,
    warmup_rounds,
    store_path,
    chunk_size,
    blosc_clevel,
    blosc_shuffle,
    blosc_cname,
    request,
):
    # pdb.set_trace()
    # if "chunk_size" == 64:
    #     pytest.skip()

    chunk_size = request.getfixturevalue(chunk_size)
    blosc_clevel = request.getfixturevalue(blosc_clevel)
    blosc_shuffle = request.getfixturevalue(blosc_shuffle)
    blosc_cname = request.getfixturevalue(blosc_cname)

    blosc_compressor = read_write_zarr.get_blosc_compressor(
        blosc_cname, blosc_clevel, blosc_shuffle
    )

    read_write_zarr.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=blosc_compressor,
    )

    compression_ratio = read_write_zarr.get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_zarr.read_zarr_array,
        args=(store_path,),
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="read")
@pytest.mark.parametrize(
    "chunk_size",
    [
        (plot_run_1_params["CHUNK_SIZE"]),
        (plot_run_2_params["CHUNK_SIZE"]),
        (plot_run_3_params["CHUNK_SIZE"]),
    ],
)
@pytest.mark.parametrize(
    "gzip_level",
    [
        (plot_run_1_params["GZIP_LEVEL"]),
        (plot_run_2_params["GZIP_LEVEL"]),
        (plot_run_3_params["GZIP_LEVEL"]),
    ],
)
def test_read_gzip(
    benchmark, image, rounds, warmup_rounds, store_path, chunk_size, gzip_level
):
    if gzip_level is None:
        pytest.skip()
    gzip_compressor = read_write_zarr.get_gzip_compressor(gzip_level)

    read_write_zarr.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=gzip_compressor,
    )

    compression_ratio = read_write_zarr.get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_zarr.read_zarr_array,
        args=(store_path,),
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="read")
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("zstd_level", ZSTD_LEVEL)
def test_read_zstd(
    benchmark, image, rounds, warmup_rounds, store_path, chunk_size, zstd_level
):
    zstd_compressor = read_write_zarr.get_zstd_compressor(zstd_level)

    read_write_zarr.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=zstd_compressor,
    )

    compression_ratio = read_write_zarr.get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_zarr.read_zarr_array,
        args=(store_path,),
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )
