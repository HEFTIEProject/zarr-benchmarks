import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
import seaborn as sns

from zarr_benchmarks import utils


def prepare_benchmarks_dataframe(json_dict: dict) -> pd.DataFrame:
    benchmark_df = pd.json_normalize(json_dict["benchmarks"])

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
    benchmark_df["compressor"] = ""
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

    # remove un-needed columns
    stats_cols = [col for col in benchmark_df if col.startswith("stats")]
    benchmark_df = benchmark_df[
        [
            "group",
            "compressor",
            "compression_level",
            "compression_ratio",
            "params.chunk_size",
            "params.blosc_shuffle",
        ]
        + stats_cols
    ]
    benchmark_df = benchmark_df.rename(
        columns={
            "params.chunk_size": "chunk_size",
            "params.blosc_shuffle": "blosc_shuffle",
        }
    )

    return benchmark_df


def get_benchmarks_dataframe(
    package_paths_dict: dict,
) -> pd.DataFrame:
    """Combine multiple pytest-benchmark json results into a single dataframe"""

    benchmark_dfs = []
    for id, json_path in package_paths_dict.items():
        benchmark_df = prepare_benchmarks_dataframe(utils.read_json_file(json_path))
        benchmark_df.insert(0, "package", id)
        benchmark_dfs.append(benchmark_df)

    return pd.concat(benchmark_dfs, ignore_index=True)


def plot_relplot_benchmarks(
    data: pd.DataFrame,
    *,
    group: str,
    x_axis: str,
    y_axis: str,
    hue: str,
    size: str,
    title: str,
    output_filename: str | None = None,
) -> None:
    graph = sns.relplot(
        data=data,
        x=x_axis,
        y=y_axis,
        hue=hue,
        style=hue,
        size=size,
        height=4,
        aspect=1.5,
    )
    x_axis_label, y_axis_label = get_axis_labels(x_axis, y_axis, group)
    graph.set_axis_labels(x_axis_label, y_axis_label)

    graph.figure.suptitle(title)
    graph.figure.subplots_adjust(top=0.9)

    if output_filename is not None:
        save_plot_as_png(
            graph,
            f"data/plots/{group}_relplot_{output_filename}.png",
        )


def plot_relplot_subplots_benchmarks(
    data: pd.DataFrame,
    *,
    group: str,
    x_axis: str,
    y_axis: str,
    hue: str,
    output_filename: str | None = None,
) -> None:
    graph = sns.relplot(
        data=data,
        x=x_axis,
        y=y_axis,
        col=hue,
        hue=hue,
        facet_kws=dict(sharex=True, sharey=True),
    )

    x_axis_label, y_axis_label = get_axis_labels(x_axis, y_axis, group)
    graph.set_axis_labels(x_axis_label, y_axis_label)

    if output_filename is not None:
        save_plot_as_png(
            graph,
            f"data/plots/{group}_subplot_relplot_{output_filename}.png",
        )


def get_axis_labels(x_axis: str, y_axis: str, group: str) -> tuple[str, str]:
    if x_axis.startswith("stats"):
        x_axis_label = f"{x_axis.split('.')[-1]} {group} time (s)"
    else:
        x_axis_label = x_axis.capitalize().replace("_", " ")

    if y_axis.startswith("stats"):
        y_axis_label = f"{y_axis.split('.')[-1]} {group} time (s)"
    else:
        y_axis_label = y_axis.capitalize().replace("_", " ")

    return x_axis_label, y_axis_label


def save_plot_as_png(grid: sns.FacetGrid, output_filename: str) -> None:
    Path(output_filename).parent.mkdir(parents=True, exist_ok=True)
    grid.savefig(output_filename, format="png", dpi=300)


def create_read_write_plots(
    zarr_v2_path: str | Path, zarr_v3_path: str | Path, tensorstore_path: str | Path
) -> None:
    package_paths_dict = {
        "zarr_python_2": zarr_v2_path,
        "zarr_python_3": zarr_v3_path,
        "tensorstore": tensorstore_path,
    }

    benchmarks_df = get_benchmarks_dataframe(
        package_paths_dict,
    )

    read_write_benchmarks = benchmarks_df[
        (benchmarks_df.chunk_size.isin([64, 128]))
        & (~benchmarks_df.blosc_shuffle.isin(["noshuffle", "bitshuffle"]))
    ]

    benchmarks_zarr_v2 = read_write_benchmarks[
        read_write_benchmarks.package == "zarr_python_2"
    ]
    write_zarr_v2 = benchmarks_zarr_v2[benchmarks_zarr_v2.group == "write"]
    read_zarr_v2 = benchmarks_zarr_v2[benchmarks_zarr_v2.group == "read"]

    write_zarr_v2_chunks_128 = write_zarr_v2[write_zarr_v2.chunk_size == 128]
    read_zarr_v2_chunks_128 = read_zarr_v2[read_zarr_v2.chunk_size == 128]

    benchmark_name = Path(zarr_v2_path).stem
    data = utils.read_json_file(Path(zarr_v2_path))
    machine_info = data["machine_info"]["machine"]
    date = datetime.now().strftime("%Y-%m-%d")

    output_filename = date + "_" + machine_info + "_" + benchmark_name
    plot_relplot_benchmarks(
        write_zarr_v2_chunks_128,
        group="write",
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        title="zarr_python_2",
        output_filename=output_filename,
    )

    plot_relplot_benchmarks(
        read_zarr_v2_chunks_128,
        group="read",
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        title="zarr_python_2",
        output_filename=output_filename,
    )

    plot_relplot_subplots_benchmarks(
        write_zarr_v2_chunks_128,
        group="write",
        x_axis="stats.mean",
        y_axis="compression_level",
        hue="compressor",
        output_filename=output_filename,
    )
    plot_relplot_subplots_benchmarks(
        read_zarr_v2_chunks_128,
        group="read",
        x_axis="stats.mean",
        y_axis="compression_level",
        hue="compressor",
        output_filename=output_filename,
    )

    print("Plotting finished 🕺")
    print("Plots saved to 'data/plots'")


def create_all_plots(
    json_dir: str, zarr_v2_id: str, zarr_v3_id: str, tensorstore_id: str
) -> None:
    json_dir_path = Path(f"data/json/{json_dir}")
    create_read_write_plots(
        json_dir_path / f"{zarr_v2_id}_zarr-python-v2.json",
        json_dir_path / f"{zarr_v3_id}_zarr-python-v3.json",
        json_dir_path / f"{tensorstore_id}_tensorstore.json",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "json_dir",
        help="name of directory inside data/json to process files from e.g. 'Windows-CPython-3.13-64bit'",
    )
    parser.add_argument("zarr_v2_id", help="id of zarr-python-v2 json file e.g. 0001")
    parser.add_argument("zarr_v3_id", help="id of zarr-python-v3 json file e.g. 0001")
    parser.add_argument("tensorstore_id", help="id of tensorstore json file e.g. 0001")
    args = parser.parse_args()

    create_all_plots(
        args.json_dir, args.zarr_v2_id, args.zarr_v3_id, args.tensorstore_id
    )
