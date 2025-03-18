from time import sleep
import imageio.v3 as iio
import pathlib
import numpy as np
import zarr
import shutil
import pytest
import timeit

# Read jpeg series
def read_image():
    
    image = get_image()

    # Create zarr array and write to it
    store_path = 'data/heart-example.zarr'
    zarr_array=write_zarr_array(image, store_path)

    # read from zarr array
    read_image = read_zarr_array(store_path)
    return read_image

def get_compression_ratio(store_path: pathlib.Path):
    zarr_array = zarr.open_array(store_path, mode='r')
    # Compression ratio
    print(zarr_array.info_complete())
    compression_ratio=zarr_array.nbytes / zarr_array.nbytes_stored()
    print(compression_ratio)
    
    return compression_ratio


def read_zarr_array(store_path: pathlib.Path):
    zarr_read = zarr.open_array(store_path, mode='r')
    read_image = zarr_read[:]
    return read_image

def write_zarr_array(image: np.array, store_path: pathlib.Path, overwrite: bool):
    # pdb.set_trace()
    
    start_time=timeit.default_timer()
    if overwrite:
        print("Overwriting is set to: ", overwrite)
        remove_output_dir(store_path)
    end_time=timeit.default_timer()
    
    removal_time=end_time-start_time
    
    print(f"Time to remove output directory: {removal_time}")
    
        
    zarr_array = zarr.create_array(
    store=store_path,
    shape=image.shape,
    chunks=(100, 100, 100),
    dtype=image.dtype
    )
    
    zarr_array[:] = image
    return zarr_array, removal_time

def get_image(image_dir_path: pathlib.Path) -> np.array:
    """Read a series of jpeg to one 3D numpy array"""
    image_slices = []
    for image_slice in image_dir_path.iterdir():
        if not image_slice.is_file():
            continue

        image_slices.append(iio.imread(image_slice))

    image = np.stack(image_slices, axis=0)
    
    return image

def remove_output_dir(output_dir: pathlib.Path):
    if output_dir.exists():
        shutil.rmtree(output_dir)
