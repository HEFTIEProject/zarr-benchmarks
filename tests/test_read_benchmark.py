import pytest
from read_write_zarr import (
    get_blosc_compressor,
    get_gzip_compressor,
    get_zstd_compressor,
    get_zarr_read_function,
    get_zarr_write_function,
    get_compression_ratio,
)
from tests.benchmark_parameters import (
    CHUNK_SIZE,
    BLOSC_CLEVEL,
    BLOSC_CNAME,
    BLOSC_SHUFFLE,
    GZIP_LEVEL,
    ZSTD_LEVEL,
)


@pytest.mark.benchmark(
    group="read",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("blosc_clevel", BLOSC_CLEVEL)
@pytest.mark.parametrize("blosc_shuffle", BLOSC_SHUFFLE)
@pytest.mark.parametrize("blosc_cname", BLOSC_CNAME)
def test_read_blosc(
    benchmark, image, store_path, chunk_size, blosc_clevel, blosc_shuffle, blosc_cname
):
    blosc_compressor = get_blosc_compressor(blosc_cname, blosc_clevel, blosc_shuffle)
    zarr_write_function = get_zarr_write_function()
    zarr_read_function = get_zarr_read_function()

    zarr_write_function(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=blosc_compressor,
    )

    compression_ratio = get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        zarr_read_function, args=(store_path,), rounds=3, warmup_rounds=1
    )


@pytest.mark.benchmark(
    group="read",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("gzip_level", GZIP_LEVEL)
def test_read_gzip(benchmark, image, store_path, chunk_size, gzip_level):
    gzip_compressor = get_gzip_compressor(gzip_level)
    zarr_write_function = get_zarr_write_function()
    zarr_read_function = get_zarr_read_function()

    zarr_write_function(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=gzip_compressor,
    )

    compression_ratio = get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        zarr_read_function, args=(store_path,), rounds=3, warmup_rounds=1
    )


@pytest.mark.benchmark(
    group="read",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("zstd_level", ZSTD_LEVEL)
def test_read_zstd(benchmark, image, store_path, chunk_size, zstd_level):
    zstd_compressor = get_zstd_compressor(zstd_level)
    zarr_write_function = get_zarr_write_function()
    zarr_read_function = get_zarr_read_function()

    zarr_write_function(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=zstd_compressor,
    )

    compression_ratio = get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        zarr_read_function, args=(store_path,), rounds=3, warmup_rounds=1
    )
