import pytest

from zarr_benchmarks.utils import remove_output_dir

read_write_tensorstore = pytest.importorskip("zarr_benchmarks.read_write_tensorstore")
pytestmark = [pytest.mark.tensorstore]


@pytest.mark.benchmark(group="write")
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
    blosc_compressor = read_write_tensorstore.get_blosc_compressor(
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
        read_write_tensorstore.write_zarr_array,
        setup=setup,
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="write")
def test_write_gzip(
    benchmark, image, rounds, warmup_rounds, store_path, chunk_size, gzip_level
):
    gzip_compressor = read_write_tensorstore.get_gzip_compressor(gzip_level)

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
        read_write_tensorstore.write_zarr_array,
        setup=setup,
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="write")
def test_write_zstd(
    benchmark, image, rounds, warmup_rounds, store_path, chunk_size, zstd_level
):
    zstd_compressor = read_write_tensorstore.get_zstd_compressor(zstd_level)

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
        read_write_tensorstore.write_zarr_array,
        setup=setup,
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )
