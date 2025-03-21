import pytest
from read_write_zarr import (
    get_zarr_write_function,
    get_blosc_compressor,
    get_gzip_compressor,
    get_zstd_compressor,
)
from utils import remove_output_dir
from tests.benchmark_parameters import (
    CHUNK_SIZE,
    BLOSC_CLEVEL,
    BLOSC_SHUFFLE,
    BLOSC_CNAME,
    GZIP_LEVEL,
    ZSTD_LEVEL,
)


@pytest.mark.benchmark(
    group="write",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("blosc_clevel", BLOSC_CLEVEL)
@pytest.mark.parametrize("blosc_shuffle", BLOSC_SHUFFLE)
@pytest.mark.parametrize("blosc_cname", BLOSC_CNAME)
def test_write_blosc(
    benchmark, image, store_path, chunk_size, blosc_clevel, blosc_shuffle, blosc_cname
):
    zarr_write_function = get_zarr_write_function()
    blosc_compressor = get_blosc_compressor(blosc_cname, blosc_clevel, blosc_shuffle)

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressor": blosc_compressor,
        }

    benchmark.pedantic(zarr_write_function, setup=setup, rounds=3, warmup_rounds=1)


@pytest.mark.benchmark(
    group="write",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("gzip_level", GZIP_LEVEL)
def test_write_gzip(benchmark, image, store_path, chunk_size, gzip_level):
    zarr_write_function = get_zarr_write_function()
    gzip_compressor = get_gzip_compressor(gzip_level)

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressor": gzip_compressor,
        }

    benchmark.pedantic(zarr_write_function, setup=setup, rounds=3, warmup_rounds=1)


@pytest.mark.benchmark(
    group="write",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("zstd_level", ZSTD_LEVEL)
def test_write_zstd(benchmark, image, store_path, chunk_size, zstd_level):
    zarr_write_function = get_zarr_write_function()
    zstd_compressor = get_zstd_compressor(zstd_level)

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressor": zstd_compressor,
        }

    benchmark.pedantic(zarr_write_function, setup=setup, rounds=3, warmup_rounds=1)
