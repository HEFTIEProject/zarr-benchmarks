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


def _fetch_from_zenodo(image_name: str) -> npt.NDArray:
    """Fetch zarr image from zenodo (if not already cached), and return as a 3D numpy array"""

    unpack = pooch.Unzip(members=[image_name])
    ZENODO.fetch(f"{image_name}.zip", processor=unpack)
    image_path = ZENODO.path / f"{image_name}.zip.unzip" / image_name

    # open zarr
    image = read_write_zarr.read_zarr_array(image_path, zarr_spec=2)

    return image


def get_heart() -> npt.NDArray:
    """Fetch image of a heart from the human organ atlas."""
    return _fetch_from_zenodo("200.64um_LADAF-2021-17_heart_complete-organ_pag.zarr")


def get_dense_segmentation() -> npt.NDArray:
    """Fetch small subset of C3 segmentation data from the H01 release"""
    return _fetch_from_zenodo("H01-c3-subset.zarr")
