import pytest

read_write_tensorstore = pytest.importorskip("zarr_benchmarks.read_write_tensorstore")
pytestmark = [pytest.mark.tensorstore]


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
    blosc_compressor = read_write_tensorstore.get_blosc_compressor(
        blosc_cname, blosc_clevel, blosc_shuffle
    )

    read_write_tensorstore.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=blosc_compressor,
    )

    compression_ratio = read_write_tensorstore.get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_tensorstore.read_zarr_array,
        args=(store_path,),
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="read")
def test_read_gzip(
    benchmark, image, rounds, warmup_rounds, store_path, chunk_size, gzip_level
):
    gzip_compressor = read_write_tensorstore.get_gzip_compressor(gzip_level)

    read_write_tensorstore.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=gzip_compressor,
    )

    compression_ratio = read_write_tensorstore.get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_tensorstore.read_zarr_array,
        args=(store_path,),
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="read")
def test_read_zstd(
    benchmark, image, rounds, warmup_rounds, store_path, chunk_size, zstd_level
):
    zstd_compressor = read_write_tensorstore.get_zstd_compressor(zstd_level)

    read_write_tensorstore.write_zarr_array(
        image=image,
        store_path=store_path,
        overwrite=True,
        chunks=(chunk_size, chunk_size, chunk_size),
        compressor=zstd_compressor,
    )

    compression_ratio = read_write_tensorstore.get_compression_ratio(store_path)
    benchmark.extra_info["compression_ratio"] = compression_ratio

    benchmark.pedantic(
        read_write_tensorstore.read_zarr_array,
        args=(store_path,),
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )
