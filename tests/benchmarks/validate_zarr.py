from pathlib import Path
from typing import Literal

import numpy.typing as npt

from zarr_benchmarks.utils import read_json_file


def _read_zarr_metadata_file(store_path: Path, zarr_spec: Literal[2, 3]) -> dict:
    if zarr_spec == 2:
        metadata_file = store_path / ".zarray"
    else:
        metadata_file = store_path / "zarr.json"

    return read_json_file(metadata_file)


def _validate_overall_settings(
    zarr_metadata: dict, image: npt.NDArray, chunk_size: int, zarr_spec: Literal[2, 3]
) -> None:
    if zarr_spec == 2:
        assert zarr_metadata["chunks"] == [chunk_size, chunk_size, chunk_size]
        assert zarr_metadata["zarr_format"] == 2
        assert zarr_metadata["shape"] == list(image.shape)
        assert zarr_metadata["dtype"] == image.dtype.str
    else:
        assert zarr_metadata["chunk_grid"]["configuration"]["chunk_shape"] == [
            chunk_size,
            chunk_size,
            chunk_size,
        ]
        assert zarr_metadata["zarr_format"] == 3
        assert zarr_metadata["shape"] == list(image.shape)
        assert zarr_metadata["data_type"] == str(image.dtype)


def validate_blosc_zarr_metadata(
    image: npt.NDArray,
    store_path: Path,
    chunk_size: int,
    blosc_clevel: int,
    blosc_shuffle: Literal["shuffle", "noshuffle", "bitshuffle"],
    blosc_cname: str,
    zarr_spec: Literal[2, 3],
) -> None:
    """Check JSON metadata of Zarr (saved at store_path) matches given image / blosc settings."""

    zarr_metadata = _read_zarr_metadata_file(store_path, zarr_spec)
    _validate_overall_settings(zarr_metadata, image, chunk_size, zarr_spec)

    # Validate specific blosc compression settings
    if zarr_spec == 2:
        compressor = zarr_metadata["compressor"]
        shuffle_values = {"noshuffle": 0, "shuffle": 1, "bitshuffle": 2}

        assert compressor["id"] == "blosc"
        assert compressor["clevel"] == blosc_clevel
        assert compressor["cname"] == blosc_cname
        assert compressor["shuffle"] == shuffle_values[blosc_shuffle]
    else:
        assert len(zarr_metadata["codecs"]) == 2
        compressor_codec = zarr_metadata["codecs"][1]

        assert compressor_codec["name"] == "blosc"
        assert compressor_codec["configuration"]["clevel"] == blosc_clevel
        assert compressor_codec["configuration"]["cname"] == blosc_cname
        assert compressor_codec["configuration"]["shuffle"] == blosc_shuffle


def validate_gzip_zarr_metadata(
    image: npt.NDArray,
    store_path: Path,
    chunk_size: int,
    gzip_level: int,
    zarr_spec: Literal[2, 3],
) -> None:
    """Check JSON metadata of Zarr (saved at store_path) matches given image / gzip settings."""

    zarr_metadata = _read_zarr_metadata_file(store_path, zarr_spec)
    _validate_overall_settings(zarr_metadata, image, chunk_size, zarr_spec)

    # Validate specific gzip compression settings
    if zarr_spec == 2:
        compressor = zarr_metadata["compressor"]
        assert compressor["id"] == "gzip"
        assert compressor["level"] == gzip_level
    else:
        assert len(zarr_metadata["codecs"]) == 2
        compressor_codec = zarr_metadata["codecs"][1]

        assert compressor_codec["name"] == "gzip"
        assert compressor_codec["configuration"]["level"] == gzip_level


def validate_zstd_zarr_metadata(
    image: npt.NDArray,
    store_path: Path,
    chunk_size: int,
    zstd_level: int,
    zarr_spec: Literal[2, 3],
) -> None:
    """Check JSON metadata of Zarr (saved at store_path) matches given image / zstd settings."""

    zarr_metadata = _read_zarr_metadata_file(store_path, zarr_spec)
    _validate_overall_settings(zarr_metadata, image, chunk_size, zarr_spec)

    # Validate specific zstd compression settings
    if zarr_spec == 2:
        compressor = zarr_metadata["compressor"]
        assert compressor["id"] == "zstd"
        assert compressor["level"] == zstd_level
    else:
        assert len(zarr_metadata["codecs"]) == 2
        compressor_codec = zarr_metadata["codecs"][1]

        assert compressor_codec["name"] == "zstd"
        assert compressor_codec["configuration"]["level"] == zstd_level


def validate_no_compressor_zarr_metadata(
    image: npt.NDArray, store_path: Path, chunk_size: int, zarr_spec: Literal[2, 3]
) -> None:
    """Check JSON metadata of Zarr (saved at store_path) matches given image / settings. There should be no metadata
    relating to compression stored in this case."""

    zarr_metadata = _read_zarr_metadata_file(store_path, zarr_spec)
    _validate_overall_settings(zarr_metadata, image, chunk_size, zarr_spec)

    # Validate that there are no compression settings
    if zarr_spec == 2:
        assert zarr_metadata["compressor"] is None
    else:
        assert len(zarr_metadata["codecs"]) == 1
        assert zarr_metadata["codecs"][0] == {
            "configuration": {"endian": "little"},
            "name": "bytes",
        }
