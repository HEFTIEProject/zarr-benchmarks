from importlib.metadata import version
from importlib.util import find_spec

# ruff: noqa: F401

# Import either zarr-python v3, zarr-python v2 or tensorstore as read_write_zarr depending on available dependencies
if find_spec("tensorstore"):
    from zarr_benchmarks.read_write_zarr import (
        read_write_tensorstore as read_write_zarr,
    )
else:
    if version("zarr").split(".")[0] == "2":
        from zarr_benchmarks.read_write_zarr import (  # type: ignore[no-redef]
            read_write_zarr_python_v2 as read_write_zarr,
        )
    else:
        from zarr_benchmarks.read_write_zarr import (  # type: ignore[no-redef]
            read_write_zarr_python_v3 as read_write_zarr,
        )
