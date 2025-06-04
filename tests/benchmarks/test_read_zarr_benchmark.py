import pytest

from zarr_benchmarks.read_write_zarr import read_write_zarr

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
):
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
def test_read_gzip(
    benchmark, image, rounds, warmup_rounds, store_path, chunk_size, gzip_level
):
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


@pytest.mark.benchmark(group="read")
def test_read_no_compressor(
    benchmark, image, rounds, warmup_rounds, store_path, chunk_size, no_compressor
):
    if not no_compressor:
        pytest.skip("config didn't include no compressor")

    read_write_zarr.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=None,
    )

    compression_ratio = read_write_zarr.get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_zarr.read_zarr_array,
        args=(store_path,),
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )
