import pdb
import imageio.v3 as iio
import pathlib
import numpy as np
import napari
import zarr
import shutil

# Read jpeg series
def read_image():
    
    image = get_image()

    # Create zarr array and write to it
    zarr_array=create_zarr_array(image)
    
    try:
        zarr_array[:] = image
    except zarr.errors.ContainsArrayError:
        print("Array already exists in the store. Overwriting...")
        zarr_array = create_zarr_array(image, overwrite=True)
        zarr_array[:] = image
    
    # Compression ratio
    print(zarr_array.info_complete())
    print(zarr_array.nbytes / zarr_array.nbytes_stored())

    # read from zarr array
    zarr_read = zarr.open_array('data/heart-example.zarr', mode='r')
    read_image = zarr_read[:]
    return read_image


def create_zarr_array(image, overwrite=True):
    # pdb.set_trace()
    store_path = 'data/heart-example.zarr'
    if overwrite and pathlib.Path(store_path).exists():
        shutil.rmtree(store_path)
    zarr_array = zarr.create_array(
    store=store_path,
    shape=image.shape,
    chunks=(100, 100, 100),
    dtype=image.dtype
    )
    return zarr_array

def get_image():
    image_slices = []
    for image_slice in pathlib.Path('data/_200.64um_LADAF-2021-17_heart_complete-organ_pag-0.10_0.03_jp2_').iterdir():
        if not image_slice.is_file():
            continue

        image_slices.append(iio.imread(image_slice))

    image = np.stack(image_slices, axis=0)
    
    return image

def test_write(benchmark):
    image = get_image()
    def write():
        create_zarr_array(image)
    benchmark(write)