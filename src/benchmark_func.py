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
        store=output_path, shape=image.shape, chunks=chunk_size, dtype=image.dtype
    )
    zarr_array[:] = image


def benchmark_write_to_zarr(
    image: np.array, output_path: Path, chunk_size: tuple[int]
) -> None:
    logger.info(f"Starting zarr write benchmarking run - chunks {chunk_size}...")

    # Ideally wouldn't include removal of any existing array in total time
    if output_path.exists():
        shutil.rmtree(output_path)

    write_to_zarr(image, output_path, chunk_size)


def run_profiling() -> None:
    # runner = pyperf.Runner(values=5, warmups=1, processes=20)
    runner = pyperf.Runner(values=2, warmups=1, processes=2)

    # image = read_image(Path("data/_200.64um_LADAF-2021-17_heart_complete-organ_pag-0.10_0.03_jp2_"))
    image = np.ones(shape=(500, 500, 500))
    output_path = Path("output/heart-example.zarr")

    chunk_sizes = [(200, 200, 200), (100, 100, 100)]
    for chunk_size in chunk_sizes:
        # Seems to be no option to exclude removal of old dir from timing using bench_func
        runner.bench_func(
            f"write_to_zarr-{chunk_size}",
            benchmark_write_to_zarr,
            image,
            output_path,
            chunk_size,
        )


if __name__ == "__main__":
    # To dump results to json, run with: python src/benchmark_func.py -o output/bench.json
    logging.basicConfig(level=logging.INFO)
    run_profiling()
