import pytest

from zarr_benchmarks.read_write_zarr import read_write_zarr
from zarr_benchmarks.utils import is_zarr_python_v2

pytestmark = [pytest.mark.tensorstore, pytest.mark.zarr_python]


@pytest.mark.benchmark(group="read")
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
    zarr_spec,
):
    if zarr_spec == 3 and is_zarr_python_v2():
        pytest.skip("Zarr v3 is not supported in the py313-zarrv2 environment.")

    blosc_compressor = read_write_zarr.get_blosc_compressor(
        blosc_cname, blosc_clevel, blosc_shuffle, zarr_spec=zarr_spec
    )

    read_write_zarr.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=blosc_compressor,
        zarr_spec=zarr_spec,
    )

    compression_ratio = read_write_zarr.get_compression_ratio(
        store_path, zarr_spec=zarr_spec
    )
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_zarr.read_zarr_array,
        args=(store_path,),
        kwargs={"zarr_spec": "zarr_spec"},
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="read")
def test_read_gzip(
    benchmark,
    image,
    rounds,
    warmup_rounds,
    store_path,
    chunk_size,
    gzip_level,
    zarr_spec,
):
    if zarr_spec == 3 and is_zarr_python_v2():
        pytest.skip("Zarr v3 is not supported in the py313-zarrv2 environment.")

    gzip_compressor = read_write_zarr.get_gzip_compressor(
        gzip_level, zarr_spec=zarr_spec
    )

    read_write_zarr.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=gzip_compressor,
        zarr_spec=zarr_spec,
    )

    compression_ratio = read_write_zarr.get_compression_ratio(
        store_path, zarr_spec=zarr_spec
    )
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_zarr.read_zarr_array,
        args=(store_path,),
        kwargs={"zarr_spec": "zarr_spec"},
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="read")
def test_read_zstd(
    benchmark,
    image,
    rounds,
    warmup_rounds,
    store_path,
    chunk_size,
    zstd_level,
    zarr_spec,
):
    if zarr_spec == 3 and is_zarr_python_v2():
        pytest.skip("Zarr v3 is not supported in the py313-zarrv2 environment.")

    zstd_compressor = read_write_zarr.get_zstd_compressor(
        zstd_level, zarr_spec=zarr_spec
    )

    read_write_zarr.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=zstd_compressor,
        zarr_spec=zarr_spec,
    )

    compression_ratio = read_write_zarr.get_compression_ratio(
        store_path, zarr_spec=zarr_spec
    )
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_zarr.read_zarr_array,
        args=(store_path,),
        kwargs={"zarr_spec": "zarr_spec"},
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="read")
def test_read_no_compressor(
    benchmark,
    image,
    rounds,
    warmup_rounds,
    store_path,
    chunk_size,
    no_compressor,
    zarr_spec,
):
    if not no_compressor:
        pytest.skip("config didn't include no compressor")

    if zarr_spec == 3 and is_zarr_python_v2():
        pytest.skip("Zarr v3 is not supported in the py313-zarrv2 environment.")

    read_write_zarr.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=None,
        zarr_spec=zarr_spec,
    )

    compression_ratio = read_write_zarr.get_compression_ratio(
        store_path, zarr_spec=zarr_spec
    )
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_zarr.read_zarr_array,
        args=(store_path,),
        kwargs={"zarr_spec": "zarr_spec"},
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )
