import pytest
from utils import remove_output_dir
from tests.benchmark_parameters import (
    CHUNK_SIZE,
    BLOSC_CLEVEL,
    BLOSC_SHUFFLE,
    BLOSC_CNAME,
    GZIP_LEVEL,
    ZSTD_LEVEL,
)

try:
    import read_write_zarr_v3 as read_write_zarr
except ImportError:
    import read_write_zarr_v2 as read_write_zarr


@pytest.mark.zarr_python
@pytest.mark.benchmark(
    group="write",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("blosc_clevel", BLOSC_CLEVEL)
@pytest.mark.parametrize("blosc_shuffle", BLOSC_SHUFFLE)
@pytest.mark.parametrize("blosc_cname", BLOSC_CNAME)
def test_write_blosc(
    benchmark,
    image,
    rounds,
    warmup_rounds,
    store_path,
    chunk_size,
    blosc_clevel,
    blosc_shuffle,
    blosc_cname,
):
    blosc_compressor = read_write_zarr.get_blosc_compressor(
        blosc_cname, blosc_clevel, blosc_shuffle
    )

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressor": blosc_compressor,
        }

    benchmark.pedantic(
        read_write_zarr.write_zarr_array,
        setup=setup,
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.zarr_python
@pytest.mark.benchmark(
    group="write",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("gzip_level", GZIP_LEVEL)
def test_write_gzip(
    benchmark, image, rounds, warmup_rounds, store_path, chunk_size, gzip_level
):
    gzip_compressor = read_write_zarr.get_gzip_compressor(gzip_level)

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressor": gzip_compressor,
        }

    benchmark.pedantic(
        read_write_zarr.write_zarr_array,
        setup=setup,
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.zarr_python
@pytest.mark.benchmark(
    group="write",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("zstd_level", ZSTD_LEVEL)
def test_write_zstd(
    benchmark, image, rounds, warmup_rounds, store_path, chunk_size, zstd_level
):
    zstd_compressor = read_write_zarr.get_zstd_compressor(zstd_level)

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressor": zstd_compressor,
        }

    benchmark.pedantic(
        read_write_zarr.write_zarr_array,
        setup=setup,
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )
