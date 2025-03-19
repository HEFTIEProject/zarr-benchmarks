import pytest
from src.read_write_zarr import write_zarr_array, remove_output_dir
import pathlib
import zarr
from tests.benchmark_parameters import (
    CHUNK_SIZE,
    BLOSC_CLEVEL,
    BLOSC_SHUFFLE,
    BLOSC_CNAME,
)


@pytest.mark.benchmark(
    group="write",
)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
@pytest.mark.parametrize("blosc_clevel", BLOSC_CLEVEL)
@pytest.mark.parametrize("blosc_shuffle", BLOSC_SHUFFLE)
@pytest.mark.parametrize("blosc_cname", BLOSC_CNAME)
def test_write_blosc(
    benchmark, image, chunk_size, blosc_clevel, blosc_shuffle, blosc_cname
):
    store_path = pathlib.Path("data/output/heart-example.zarr")

    def setup():
        remove_output_dir(store_path)
        return (), {
            "image": image,
            "store_path": store_path,
            "overwrite": False,
            "chunks": (chunk_size, chunk_size, chunk_size),
            "compressors": zarr.codecs.BloscCodec(
                cname=blosc_cname, clevel=blosc_clevel, shuffle=blosc_shuffle
            ),
        }

    benchmark.pedantic(write_zarr_array, setup=setup, rounds=3, warmup_rounds=1)


# @pytest.mark.benchmark(
#     group="write",
# )
# @pytest.mark.parametrize("chunk_size", CHUNK_SIZE)
# def test_write_gzip(benchmark, image, chunk_size, compressors):
#     store_path = pathlib.Path("data/output/heart-example.zarr")
#     overwrite = False

#     def setup():
#         remove_output_dir(store_path)
#         return (
#             image,
#             store_path,
#             overwrite,
#             (chunk_size, chunk_size, chunk_size),
#             compressors,
#         ), {}

#     benchmark.pedantic(write_zarr_array, setup=setup, rounds=3, warmup_rounds=1)
