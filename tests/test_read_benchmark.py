import pytest
from src.read_write_zarr import write_zarr_array, read_zarr_array, get_compression_ratio
from tests.benchmark_parameters import (
    CHUNK_SIZE,
    BLOSC_CLEVEL,
    BLOSC_CNAME,
    BLOSC_SHUFFLE,
    GZIP_LEVEL,
    ZSTD_LEVEL,
)
import pathlib
import zarr


@pytest.mark.benchmark(
    group="read",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("blosc_clevel", BLOSC_CLEVEL)
@pytest.mark.parametrize("blosc_shuffle", BLOSC_SHUFFLE)
@pytest.mark.parametrize("blosc_cname", BLOSC_CNAME)
def test_read_blosc(
    benchmark, image, chunk_size, blosc_clevel, blosc_shuffle, blosc_cname
):
    store_path = pathlib.Path("data/output/heart-example.zarr")

    write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressors=zarr.codecs.BloscCodec(
            cname=blosc_cname, clevel=blosc_clevel, shuffle=blosc_shuffle
        ),
    )

    compression_ratio = get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(read_zarr_array, args=(store_path,), rounds=3, warmup_rounds=1)


@pytest.mark.benchmark(
    group="read",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("gzip_level", GZIP_LEVEL)
def test_read_gzip(benchmark, image, chunk_size, gzip_level):
    store_path = pathlib.Path("data/output/heart-example.zarr")

    write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressors=zarr.codecs.GzipCodec(level=gzip_level),
    )

    compression_ratio = get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(read_zarr_array, args=(store_path,), rounds=3, warmup_rounds=1)


@pytest.mark.benchmark(
    group="read",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("zstd_level", ZSTD_LEVEL)
def test_read_zstd(benchmark, image, chunk_size, zstd_level):
    store_path = pathlib.Path("data/output/heart-example.zarr")

    write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressors=zarr.codecs.ZstdCodec(level=zstd_level),
    )

    compression_ratio = get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(read_zarr_array, args=(store_path,), rounds=3, warmup_rounds=1)
