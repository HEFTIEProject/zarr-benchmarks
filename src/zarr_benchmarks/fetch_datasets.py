import numpy.typing as npt
import pooch

from zarr_benchmarks.read_write_zarr import read_write_zarr

ZENODO = pooch.create(
    # Use the default cache folder for the operating system
    path=pooch.os_cache("zarr-benchmarks"),
    base_url="doi:10.5281/zenodo.15544055",
    registry=None,
)
ZENODO.load_registry_from_doi()


def get_image() -> npt.NDArray:
    """Fetch zarr image from zenodo (if not already cached), and return as a 3D numpy array"""

    heart_image = "200.64um_LADAF-2021-17_heart_complete-organ_pag.zarr"
    unpack = pooch.Unzip(members=[heart_image])
    ZENODO.fetch(f"{heart_image}.zip", processor=unpack)
    heart_image_path = ZENODO.path / f"{heart_image}.zip.unzip" / heart_image

    # open zarr
    image = read_write_zarr.read_zarr_array(heart_image_path, zarr_spec=2)

    return image
