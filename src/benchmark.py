import pyperf
from pathlib import Path
import imageio.v3 as iio
import numpy as np
import zarr
import shutil
import logging

logger = logging.getLogger(__name__)


def read_image(image_dir_path: Path) -> np.array:
    """Read a series of jpeg to one 3D numpy array"""
    image_slices = []
    for image_slice in image_dir_path.iterdir():
        if not image_slice.is_file():
            continue

        image_slices.append(iio.imread(image_slice))

    return np.stack(image_slices, axis=0)


def write_to_zarr(image: np.array, output_path: Path, chunk_size: tuple[int]) -> None:
    zarr_array = zarr.create_array(
            store=output_path,
            shape=image.shape,
            chunks=chunk_size,
            dtype=image.dtype
        )
    zarr_array[:] = image


def benchmark_write_to_zarr(loops: int, image: np.array, output_path: Path, chunk_size: tuple[int]) -> float:

    logger.info(f"Starting zarr write benchmarking run - chunks {chunk_size}...")

    total_time_for_loops = 0

    for _ in range(loops):

        # Don't include removal of any existing array in total time
        if output_path.exists():
            shutil.rmtree(output_path)

        start_time = pyperf.perf_counter()
        write_to_zarr(image, output_path, chunk_size)
        end_time = pyperf.perf_counter()

        total_time_for_loops += (end_time - start_time)

    logger.info(f"Finished zarr write benchmarking run - chunks {chunk_size} in {total_time_for_loops}")

    return total_time_for_loops


def benchmark_read_from_zarr(loops: int, image: np.array, zarr_dir_path: Path, chunk_size: tuple[int]) -> np.array:
    logger.info(f"Starting zarr read benchmarking run {chunk_size}...")

    # Write zarr image with required specification
    if zarr_dir_path.exists():
        shutil.rmtree(zarr_dir_path)
    write_to_zarr(image, zarr_dir_path, chunk_size)

    start_time = pyperf.perf_counter()

    for _ in range(loops):
        zarr_array = zarr.open_array(zarr_dir_path, mode='r')
        image = zarr_array[:]
    
    end_time = pyperf.perf_counter()
    total_time_for_loops = (end_time - start_time)

    logger.info(f"Finished zarr read benchmarking run {zarr_array.chunks} in {total_time_for_loops}")

    return total_time_for_loops


def run_profiling():
    # runner = pyperf.Runner(values=5, warmups=1, processes=20)
    runner = pyperf.Runner(values=2, warmups=1, processes=2)

    # image = read_image(Path("data/_200.64um_LADAF-2021-17_heart_complete-organ_pag-0.10_0.03_jp2_"))
    image = np.ones(shape=(500, 500, 500))
    output_path = Path("output/heart-example.zarr")

    chunk_sizes = [(200, 200, 200), (100, 100, 100)]
    for chunk_size in chunk_sizes:
        runner.bench_time_func(f"write_to_zarr-{chunk_size}", benchmark_write_to_zarr, image, output_path, chunk_size)
        runner.bench_time_func(f"read_from_zarr-{chunk_size}", benchmark_read_from_zarr, image, output_path, chunk_size)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_profiling()