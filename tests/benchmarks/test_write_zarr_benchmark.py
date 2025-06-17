import pytest

from zarr_benchmarks.read_write_zarr import read_write_zarr
from zarr_benchmarks.utils import is_zarr_python_v2, remove_output_dir

pytestmark = [pytest.mark.tensorstore, pytest.mark.zarr_python]


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
    zarr_spec,
):
    if zarr_spec == 3 and is_zarr_python_v2():
        pytest.skip("Zarr spec v3 is not supported by zarr-python v2")
    blosc_compressor = read_write_zarr.get_blosc_compressor(
        blosc_cname, blosc_clevel, blosc_shuffle, zarr_spec=zarr_spec
    )

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressor": blosc_compressor,
            "zarr_spec": zarr_spec,
        }

    benchmark.pedantic(
        read_write_zarr.write_zarr_array,
        setup=setup,
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="write")
def test_write_gzip(
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
        pytest.skip("Zarr spec v3 is not supported by zarr-python v2")
    gzip_compressor = read_write_zarr.get_gzip_compressor(
        gzip_level, zarr_spec=zarr_spec
    )

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressor": gzip_compressor,
            "zarr_spec": zarr_spec,
        }

    benchmark.pedantic(
        read_write_zarr.write_zarr_array,
        setup=setup,
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="write")
def test_write_zstd(
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
        pytest.skip("Zarr spec v3 is not supported by zarr-python v2")
    zstd_compressor = read_write_zarr.get_zstd_compressor(
        zstd_level, zarr_spec=zarr_spec
    )

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressor": zstd_compressor,
            "zarr_spec": zarr_spec,
        }

    benchmark.pedantic(
        read_write_zarr.write_zarr_array,
        setup=setup,
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )


@pytest.mark.benchmark(group="write")
def test_write_no_compressor(
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
        pytest.skip("Zarr spec v3 is not supported by zarr-python v2")

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressor": None,
            "zarr_spec": zarr_spec,
        }

    benchmark.pedantic(
        read_write_zarr.write_zarr_array,
        setup=setup,
        rounds=rounds,
        warmup_rounds=warmup_rounds,
    )
