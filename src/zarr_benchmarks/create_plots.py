import argparse
from pathlib import Path
from typing import Literal

import pandas as pd

from zarr_benchmarks import utils
from zarr_benchmarks.plotting_functions import (
    plot_catplot_benchmarks,
    plot_errorbars_benchmarks,
    plot_relplot_benchmarks,
)


def prepare_benchmarks_dataframe(json_dict: dict) -> pd.DataFrame:
    """Prepare a pandas DataFrame from the pytest-benchmark json results.
    Args:
        json_dict (dict): the json dictionary from the pytest-benchmark results.
    Returns:
        pd.DataFrame: a DataFrame with the relevant benchmark data.
    """
    benchmark_df = pd.json_normalize(json_dict["benchmarks"])
    benchmark_df["machine"] = json_dict["machine_info"]["system"]

    # copy compression ratio from read benchmarks to write benchmarks
    param_cols = [col for col in benchmark_df if col.startswith("params")]
    benchmark_df["compression_ratio"] = benchmark_df.groupby(
        param_cols, dropna=False, as_index=False
    )["extra_info.compression_ratio"].transform("max")

    # combine compression level columns for different compressors
    benchmark_df["compression_level"] = benchmark_df[
        ["params.blosc_clevel", "params.gzip_level", "params.zstd_level"]
    ].max(axis=1)

    # create column for type of compressor
    benchmark_df["compressor"] = None
    blosc_compressors = (
        "blosc-"
        + benchmark_df.loc[
            ~benchmark_df["params.blosc_clevel"].isna(), "params.blosc_cname"
        ]
    )
    benchmark_df.loc[~benchmark_df["params.blosc_clevel"].isna(), "compressor"] = (
        blosc_compressors
    )
    benchmark_df.loc[~benchmark_df["params.gzip_level"].isna(), "compressor"] = "gzip"
    benchmark_df.loc[~benchmark_df["params.zstd_level"].isna(), "compressor"] = "zstd"

    if "params.no_compressor" in benchmark_df:
        benchmark_df.loc[~benchmark_df["params.no_compressor"].isna(), "compressor"] = (
            "none"
        )

        # Give 'no compressor' rows an arbitrary compression level, so they can be shown on plots where point size is
        # related to compression level
        benchmark_df.loc[benchmark_df["compressor"] == "none", "compression_level"] = 19

    # remove un-needed columns
    stats_cols = [col for col in benchmark_df if col.startswith("stats")]
    # if "params.zarr_spec" not in benchmark_df.columns:
    #     benchmark_df["params.zarr_spec"] = 0
    benchmark_df = benchmark_df[
        [
            "machine",
            "group",
            "compressor",
            "compression_level",
            "compression_ratio",
            "params.chunk_size",
            "params.blosc_shuffle",
            "params.zarr_spec",
        ]
        + stats_cols
    ]
    benchmark_df = benchmark_df.rename(
        columns={
            "params.chunk_size": "chunk_size",
            "params.blosc_shuffle": "blosc_shuffle",
            "params.zarr_spec": "zarr_spec",
        }
    )

    return benchmark_df


def get_benchmarks_dataframe(package_paths_dict: dict) -> pd.DataFrame:
    """Combine multiple pytest-benchmark json results into a single dataframe"""

    benchmark_dfs = []
    for id, json_path in package_paths_dict.items():
        benchmark_df = prepare_benchmarks_dataframe(utils.read_json_file(json_path))
        benchmark_df.insert(0, "package", id)
        benchmark_dfs.append(benchmark_df)

    return pd.concat(benchmark_dfs, ignore_index=True)


def create_shuffle_plots(
    benchmarks_df: pd.DataFrame, plots_dir: Path, zarr_spec: Literal[2, 3]
) -> None:
    shuffle_benchmarks = benchmarks_df[
        (benchmarks_df.compressor == "blosc-zstd")
        & (benchmarks_df.compression_level == 3)
        & (benchmarks_df.chunk_size == 128)
    ]
    save_dir = plots_dir / "shuffle" / f"spec_{zarr_spec}"
    write = shuffle_benchmarks[
        (shuffle_benchmarks.group == "write")
        & (shuffle_benchmarks.package == "tensorstore")
    ]
    write = write[write.zarr_spec == 2]
    read = shuffle_benchmarks[
        (shuffle_benchmarks.group == "read")
        & (shuffle_benchmarks.package == "tensorstore")
    ]
    read = read[read.zarr_spec == 2]
    title = f"Spec v{zarr_spec} Shuffle for tensorstore - blosc-zstd"

    plot_catplot_benchmarks(
        data=read,
        x_axis="blosc_shuffle",
        y_axis="compression_ratio",
        plots_dir=save_dir,
        plot_name="compression_ratio",
        title=title,
    )

    plot_catplot_benchmarks(
        data=write,
        x_axis="blosc_shuffle",
        y_axis="stats.mean",
        plots_dir=save_dir,
        plot_name="write",
        title=title,
    )

    plot_catplot_benchmarks(
        data=read,
        x_axis="blosc_shuffle",
        y_axis="stats.mean",
        plots_dir=save_dir,
        plot_name="read",
        title=title,
    )


def create_chunk_size_plots(
    benchmarks_df: pd.DataFrame, plots_dir: Path, zarr_spec: Literal[2, 3]
) -> None:
    chunk_size_benchmarks = benchmarks_df[
        (benchmarks_df.compressor == "blosc-zstd")
        & (benchmarks_df.compression_level == 3)
        & (benchmarks_df.blosc_shuffle == "shuffle")
    ]

    chunk_size_write = chunk_size_benchmarks[chunk_size_benchmarks.group == "write"]
    chunk_size_read = chunk_size_benchmarks[chunk_size_benchmarks.group == "read"]
    save_dir = plots_dir / "chunk_size" / f"spec_{zarr_spec}"

    chunk_size_write = chunk_size_write[chunk_size_write.zarr_spec == zarr_spec]
    chunk_size_read = chunk_size_read[chunk_size_read.zarr_spec == zarr_spec]

    plot_relplot_benchmarks(
        chunk_size_read,
        x_axis="chunk_size",
        y_axis="compression_ratio",
        col="package",
        plots_dir=save_dir,
        plot_name="compression_ratio",
        title=f"Spec_v{zarr_spec}",
    )

    plot_relplot_benchmarks(
        chunk_size_write,
        y_axis="stats.mean",
        x_axis="chunk_size",
        col="package",
        plots_dir=save_dir,
        plot_name="write",
        title=f"Spec_v{zarr_spec}",
    )

    plot_relplot_benchmarks(
        chunk_size_write,
        y_axis="stats.mean",
        x_axis="chunk_size",
        hue="package",
        title=f"Spec_v{zarr_spec}_chunk_size_write_all",
        plots_dir=save_dir,
        plot_name="write",
    )

    plot_relplot_benchmarks(
        chunk_size_read,
        y_axis="stats.mean",
        x_axis="chunk_size",
        col="package",
        plots_dir=save_dir,
        plot_name="read",
        title=f"Spec_v{zarr_spec}",
    )

    plot_relplot_benchmarks(
        chunk_size_read,
        y_axis="stats.mean",
        x_axis="chunk_size",
        hue="package",
        title=f"Spec_v{zarr_spec}_chunk_size_read_all",
        plots_dir=save_dir,
        plot_name="read",
    )


def create_read_write_errorbar_plots_for_package(
    read_write_benchmarks: pd.DataFrame,
    package: str,
    plots_dir: Path,
    zarr_spec: Literal[2, 3],
) -> None:
    package_benchmarks = read_write_benchmarks[read_write_benchmarks.package == package]
    write = package_benchmarks[package_benchmarks.group == "write"]
    read = package_benchmarks[package_benchmarks.group == "read"]

    write_chunks_128 = write[write.chunk_size == 128]
    read_chunks_128 = read[read.chunk_size == 128]

    write_chunks_128 = write_chunks_128[write_chunks_128.zarr_spec == zarr_spec]
    read_chunks_128 = read_chunks_128[read_chunks_128.zarr_spec == zarr_spec]

    if write_chunks_128.empty or read_chunks_128.empty:
        print(
            f"Skipping read_write plots for {package}, as no data for zarr spec v{zarr_spec}"
        )
        return

    plot_errorbars_benchmarks(
        write_chunks_128,
        hue="compressor",
        col="compressor",
        size="compression_level",
        title=f"Spec_v{zarr_spec}_{package}_chunk_size128",
        plots_dir=plots_dir / "write_errorbars" / f"spec_{zarr_spec}",
        plot_name=f"Spec_v{zarr_spec}_{package}_chunk_size128",
    )

    plot_errorbars_benchmarks(
        read_chunks_128,
        hue="compressor",
        col="compressor",
        size="compression_level",
        title=f"Spec_v{zarr_spec}_{package}_chunk_size128",
        plots_dir=plots_dir / "read_errorbars" / f"spec_{zarr_spec}",
        plot_name=f"Spec_v{zarr_spec}_{package}_chunk_size128",
    )


def create_read_write_plots_for_package(
    read_write_benchmarks: pd.DataFrame,
    package: str,
    plots_dir: Path,
    zarr_spec: Literal[2, 3],
) -> None:
    package_benchmarks = read_write_benchmarks[read_write_benchmarks.package == package]

    write = package_benchmarks[package_benchmarks.group == "write"]
    read = package_benchmarks[package_benchmarks.group == "read"]

    write = write[write.zarr_spec == zarr_spec]
    read = read[read.zarr_spec == zarr_spec]

    if write.empty or read.empty:
        print(
            f"Skipping read_write plots for {package}, as no data for zarr spec v{zarr_spec}"
        )
        return

    plot_relplot_benchmarks(
        write,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        col="chunk_size",
        title=f"Spec_{zarr_spec}_{package}_chunk_size_all",
        plots_dir=plots_dir / "write" / f"spec_{zarr_spec}",
        plot_name=f"{package}_chunk_size_all",
    )

    plot_relplot_benchmarks(
        read,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        col="chunk_size",
        title=f"Spec_{zarr_spec}_{package}_chunk_size_all",
        plots_dir=plots_dir / "read" / f"spec_{zarr_spec}",
        plot_name=f"{package}_chunk_size_all",
    )

    write_chunks_128 = write[write.chunk_size == 128]
    read_chunks_128 = read[read.chunk_size == 128]

    write_chunks_128 = write_chunks_128[write_chunks_128.zarr_spec == zarr_spec]
    read_chunks_128 = read_chunks_128[read_chunks_128.zarr_spec == zarr_spec]

    plot_relplot_benchmarks(
        write_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        title=f"Spec_v2_{package}_chunk_size128",
        plots_dir=plots_dir / "write",
        plot_name=f"{package}_chunk_size128",
    )

    plot_relplot_benchmarks(
        read_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        title=f"Spec_v2_{package}_chunk_size128",
        plots_dir=plots_dir / "read",
        plot_name=f"{package}_chunk_size128",
    )

    plot_relplot_benchmarks(
        write_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        col="compressor",
        title="Spec_v2",
        plots_dir=plots_dir / "write",
        plot_name=f"{package}_chunk_size128",
    )

    plot_relplot_benchmarks(
        read_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        col="compressor",
        title="Spec_v2",
        plots_dir=plots_dir / "read",
        plot_name=f"{package}_chunk_size128",
    )


def create_read_write_plots(
    benchmarks_df: pd.DataFrame, plots_dir: Path, zarr_spec: Literal[2, 3]
) -> None:
    read_write_benchmarks = benchmarks_df[
        (benchmarks_df.chunk_size.isin([64, 128]))
        & (~benchmarks_df.blosc_shuffle.isin(["noshuffle", "bitshuffle"]))
    ]

    create_read_write_plots_for_package(
        read_write_benchmarks, "zarr_python_2", plots_dir, zarr_spec
    )
    create_read_write_plots_for_package(
        read_write_benchmarks, "zarr_python_3", plots_dir, zarr_spec
    )
    create_read_write_plots_for_package(
        read_write_benchmarks, "tensorstore", plots_dir, zarr_spec
    )

    create_read_write_errorbar_plots_for_package(
        read_write_benchmarks, "zarr_python_2", plots_dir, zarr_spec
    )
    create_read_write_errorbar_plots_for_package(
        read_write_benchmarks, "zarr_python_3", plots_dir, zarr_spec
    )
    create_read_write_errorbar_plots_for_package(
        read_write_benchmarks, "tensorstore", plots_dir, zarr_spec
    )

    read_chunks_128 = read_write_benchmarks[
        (read_write_benchmarks.group == "read")
        & (read_write_benchmarks.chunk_size == 128)
        & (read_write_benchmarks.zarr_spec == zarr_spec)
    ]
    write_chunks_128 = read_write_benchmarks[
        (read_write_benchmarks.group == "write")
        & (read_write_benchmarks.chunk_size == 128)
        & (read_write_benchmarks.zarr_spec == zarr_spec)
    ]

    plot_relplot_benchmarks(
        read_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        col="package",
        hue="compressor",
        size="compression_level",
        plots_dir=plots_dir / "read" / f"spec_{zarr_spec}",
        plot_name="all_packages",
        title=f"Spec_v{zarr_spec}",
    )

    plot_relplot_benchmarks(
        write_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        col="package",
        hue="compressor",
        size="compression_level",
        plots_dir=plots_dir / "write" / f"spec_{zarr_spec}",
        plot_name="all_packages",
        title=f"Spec_v{zarr_spec}",
    )


def create_plots_for_image(image_dir: Path, json_ids: list[str] | None) -> None:
    """Create all plots for benchmark results from a single image."""

    results_path = image_dir

    # check for pytest-benchmarks's auto-generated sub-dir e.g. Windows-CPython-3.13-64bit
    sub_dirs = [sub_path for sub_path in image_dir.iterdir() if sub_path.is_dir()]
    if len(sub_dirs) > 1:
        raise ValueError(f"Expected only one sub-directory inside {image_dir}")
    if len(sub_dirs) == 1:
        results_path = sub_dirs[0]

    print(f"📈 Generating plots from results in {results_path}...")

    if json_ids is None:
        # Find the latest 3 json ids in the sub-dir
        all_ids = []
        for result_json in results_path.glob("*.json"):
            all_ids.append(result_json.stem.split("_")[0])

        json_ids = sorted(all_ids)[-3:]

    zarr_v2_path = results_path / f"{json_ids[0]}_zarr-python-v2.json"
    zarr_v3_path = results_path / f"{json_ids[1]}_zarr-python-v3.json"
    tensorstore_path = results_path / f"{json_ids[2]}_tensorstore.json"

    package_paths_dict = {
        "zarr_python_2": zarr_v2_path,
        "zarr_python_3": zarr_v3_path,
        "tensorstore": tensorstore_path,
    }

    benchmarks_df = get_benchmarks_dataframe(
        package_paths_dict,
    )

    plots_dir = Path(__file__).parents[2] / "data" / "plots" / image_dir.stem
    create_read_write_plots(benchmarks_df, plots_dir, zarr_spec=2)
    create_read_write_plots(benchmarks_df, plots_dir, zarr_spec=3)
    create_chunk_size_plots(benchmarks_df, plots_dir, zarr_spec=2)
    create_chunk_size_plots(benchmarks_df, plots_dir, zarr_spec=3)
    create_shuffle_plots(benchmarks_df, plots_dir, zarr_spec=2)
    create_shuffle_plots(benchmarks_df, plots_dir, zarr_spec=3)

    print("Plotting finished 🕺")
    print(f"Plots saved to {plots_dir}")


def create_all_plots(
    json_ids: list[str] | None = None, example_results: bool = False
) -> None:
    """Create plots for all images. By default, process the latest benchmark results inside data/results. Set
    example_results to process from the example_results/ directory instead.
    Args:
        json_ids (list[str] | None, optional): optional list of json ids e.g. ["0001", "0002", "0003"] of the
            zarr-python-v2, zarr-python-v3 and tensorstore json to process. The same ids will be used for all image
            sub-directories.
        example_results (bool, optional): whether to process jsons from example_results/ rather than data/results.
    """

    if example_results:
        result_path = Path(__file__).parents[2] / "example_results"
    else:
        result_path = Path(__file__).parents[2] / "data" / "results"

    image_dirs = [sub_path for sub_path in result_path.iterdir() if sub_path.is_dir()]
    for image_dir in image_dirs:
        create_plots_for_image(image_dir, json_ids)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create plots from benchmark results. By default, processes the latest benchmark results for "
        "all images from data/results. Plots are written to sub-directories of `data/plots`, with names matching the "
        "image sub-directories in data/results. To override these defaults, provide --json_ids and/or --example_results."
    )
    parser.add_argument(
        "--json_ids",
        nargs=3,
        metavar="JSON_ID",
        help="provide the ids of the zarr-python-v2, zarr-python-v3 and tensorstore json files you want to process "
        "e.g. 0001 0002 0003. This uses the same ids for all image sub-directories.",
    )
    parser.add_argument(
        "--example_results",
        help="Process files from the example_results/ directory (rather than data/results default).",
        action="store_true",
    )
    args = parser.parse_args()

    create_all_plots(args.json_ids, args.example_results)
