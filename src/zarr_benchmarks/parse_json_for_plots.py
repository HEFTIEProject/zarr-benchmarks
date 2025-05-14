import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from zarr_benchmarks import utils


def prepare_benchmarks_dataframe(json_dict: dict) -> pd.DataFrame:
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
            "machine",
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
    x_axis: str,
    y_axis: str,
    sub_dir_name: str,
    plot_name: str,
    title: str | None = None,
    hue: str | None = None,
    size: str | None = None,
    col: str | None = None,
) -> None:
    """Generate a scatter plot using seaborn's relplot function with a dataframe as input.
    Calls a function to save the plot as a PNG file.

    Args:
        data (pd.DataFrame): Contains the data to be plotted.
        x_axis (str): name of dataframe column to be used for x-axis
        y_axis (str): name of dataframe column to be used for y-axis
        sub_dir_name (str): name of the sub-directory where the plot will be saved within data/plots
        plot_name (str): name of the plot which will be used for the start of the final filename
        title (str | None, optional): title of the plot. Defaults to None.
        hue (str | None, optional): name of dataframe column to be used for the colours in the plot. Defaults to None.
        size (str | None, optional): name of dataframe column to be used for size of datapoints. Defaults to None.
        col (str | None, optional): name of dataframe column to be used for splitting into subplots. Defaults to None.
    """
    if col is None:
        facet_kws = None
        col_wrap = None
        plot_name = plot_name
    else:
        facet_kws = dict(sharex=True, sharey=True)
        if len(data[col].unique()) < 3:
            col_wrap = 2
        else:
            col_wrap = 3
        plot_name = plot_name + "_subplots"

    graph = sns.relplot(
        data=data,
        x=x_axis,
        y=y_axis,
        hue=hue,
        style=hue,
        size=size,
        col=col,
        height=4,
        aspect=1.5,
        facet_kws=facet_kws,
        col_wrap=col_wrap,
    )
    x_axis_label, y_axis_label = get_axis_labels(data, x_axis=x_axis, y_axis=y_axis)
    [x_min, x_max] = graph.data[x_axis].min(), graph.data[x_axis].max()

    if x_max / x_min > 10:
        graph.set(xscale="log")
    graph.set_axis_labels(x_axis_label, y_axis_label)

    if title is not None:
        graph.figure.suptitle(title)
        graph.tight_layout()

    save_plot_as_png(
        graph,
        get_output_path(data, sub_dir_name, plot_name),
    )


def get_axis_labels(
    benchmark_df: pd.DataFrame, *, x_axis: str, y_axis: str
) -> tuple[str, str]:
    group = benchmark_df.group.unique()
    if len(group) != 1:
        raise ValueError("Expected only one group value in dataframe")

    if x_axis.startswith("stats"):
        x_axis_label = f"{x_axis.split('.')[-1]} {group[0]} time (s)"
    else:
        x_axis_label = x_axis.capitalize().replace("_", " ")

    if y_axis.startswith("stats"):
        y_axis_label = f"{y_axis.split('.')[-1]} {group[0]} time (s)"
    else:
        y_axis_label = y_axis.capitalize().replace("_", " ")

    return x_axis_label, y_axis_label


def get_output_path(
    benchmarks_df: pd.DataFrame, sub_dir_name: str, plot_name: str
) -> Path:
    machine_info = benchmarks_df["machine"].iloc[0]
    date = datetime.now().strftime("%Y-%m-%d")

    plots_dir = Path(__file__).parents[2] / "data" / "plots" / sub_dir_name
    return plots_dir / f"{plot_name}_{date}_{machine_info}.png"


def save_plot_as_png(grid: sns.FacetGrid, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    grid.savefig(output_path, format="png", dpi=300)
    plt.close()


def plot_catplot_benchmarks(
    data: pd.DataFrame,
    *,
    x_axis: str,
    y_axis: str,
    sub_dir_name: str,
    plot_name: str,
    title: str | None = None,
    hue: str | None = None,
) -> None:
    """Generate a bar plot using seaborn's catplot function with a dataframe as input.
    Calls a function to save the plot as a PNG file.


    Args:
        data (pd.DataFrame): Contains the data to be plotted.
        x_axis (str): name of dataframe column to be used for x-axis
        y_axis (str): name of dataframe column to be used for y-axis
        sub_dir_name (str): name of the sub-directory where the plot will be saved within data/plots
        plot_name (str): name of the plot which will be used for the start of the final filename
        title (str | None, optional): title of the plot. Defaults to None.
        hue (str | None, optional): name of dataframe column to be used for the colours in the plot. Defaults to None.
    """
    graph = sns.catplot(
        data=data,
        x=x_axis,
        y=y_axis,
        hue=hue,
        kind="bar",
        height=4,
        aspect=1.5,
    )
    x_axis_label, y_axis_label = get_axis_labels(data, x_axis=x_axis, y_axis=y_axis)
    graph.set_axis_labels(x_axis_label, y_axis_label)

    if title is not None:
        graph.figure.suptitle(title)
        graph.tight_layout()

    save_plot_as_png(
        graph,
        get_output_path(data, sub_dir_name, plot_name),
    )


def create_shuffle_plots(
    benchmarks_df: pd.DataFrame,
) -> None:
    shuffle_benchmarks = benchmarks_df[
        (benchmarks_df.compressor == "blosc-zstd")
        & (benchmarks_df.compression_level == 3)
        & (benchmarks_df.chunk_size == 128)
    ]
    sub_dir_name = "shuffle"

    write = shuffle_benchmarks[shuffle_benchmarks.group == "write"]
    read = shuffle_benchmarks[shuffle_benchmarks.group == "read"]

    plot_catplot_benchmarks(
        data=read,
        x_axis="blosc_shuffle",
        y_axis="compression_ratio",
        sub_dir_name=sub_dir_name,
        plot_name="compression_ratio",
        hue="package",
    )

    plot_catplot_benchmarks(
        data=write,
        x_axis="blosc_shuffle",
        y_axis="stats.mean",
        sub_dir_name=sub_dir_name,
        plot_name="write",
        hue="package",
    )

    plot_catplot_benchmarks(
        data=read,
        x_axis="blosc_shuffle",
        y_axis="stats.mean",
        sub_dir_name=sub_dir_name,
        plot_name="read",
        hue="package",
    )


def create_chunk_size_plots(
    benchmarks_df: pd.DataFrame,
) -> None:
    chunk_size_benchmarks = benchmarks_df[
        (benchmarks_df.compressor == "blosc-zstd")
        & (benchmarks_df.compression_level == 3)
        & (benchmarks_df.blosc_shuffle == "shuffle")
    ]

    chunk_size_write = chunk_size_benchmarks[chunk_size_benchmarks.group == "write"]
    chunk_size_read = chunk_size_benchmarks[chunk_size_benchmarks.group == "read"]

    plot_relplot_benchmarks(
        chunk_size_read,
        x_axis="chunk_size",
        y_axis="compression_ratio",
        col="package",
        sub_dir_name="chunk_size",
        plot_name="compression_ratio",
    )

    plot_relplot_benchmarks(
        chunk_size_write,
        y_axis="stats.mean",
        x_axis="chunk_size",
        col="package",
        sub_dir_name="chunk_size",
        plot_name="write",
    )

    plot_relplot_benchmarks(
        chunk_size_write,
        y_axis="stats.mean",
        x_axis="chunk_size",
        hue="package",
        title="chunk_size_write_all",
        sub_dir_name="chunk_size",
        plot_name="write",
    )

    plot_relplot_benchmarks(
        chunk_size_read,
        y_axis="stats.mean",
        x_axis="chunk_size",
        col="package",
        sub_dir_name="chunk_size",
        plot_name="read",
    )

    plot_relplot_benchmarks(
        chunk_size_read,
        y_axis="stats.mean",
        x_axis="chunk_size",
        hue="package",
        title="chunk_size_read_all",
        sub_dir_name="chunk_size",
        plot_name="read",
    )


def create_read_write_plots_for_package(
    read_write_benchmarks: pd.DataFrame, package: str
) -> None:
    package_benchmarks = read_write_benchmarks[read_write_benchmarks.package == package]
    write = package_benchmarks[package_benchmarks.group == "write"]
    read = package_benchmarks[package_benchmarks.group == "read"]

    plot_relplot_benchmarks(
        write,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        col="chunk_size",
        title=f"{package}_chunk_size_all",
        sub_dir_name="write",
        plot_name=f"{package}_chunk_size_all",
    )

    plot_relplot_benchmarks(
        read,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        col="chunk_size",
        title=f"{package}_chunk_size_all",
        sub_dir_name="read",
        plot_name=f"{package}_chunk_size_all",
    )

    write_chunks_128 = write[write.chunk_size == 128]
    read_chunks_128 = read[read.chunk_size == 128]

    plot_relplot_benchmarks(
        write_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        title=f"{package}_chunk_size128",
        sub_dir_name="write",
        plot_name=f"{package}_chunk_size128",
    )

    plot_relplot_benchmarks(
        read_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        title=f"{package}_chunk_size128",
        sub_dir_name="read",
        plot_name=f"{package}_chunk_size128",
    )

    plot_relplot_benchmarks(
        write_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        col="compressor",
        sub_dir_name="write",
        plot_name=f"{package}_chunk_size128",
    )

    plot_relplot_benchmarks(
        read_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        col="compressor",
        sub_dir_name="read",
        plot_name=f"{package}_chunk_size128",
    )


def create_read_write_plots(benchmarks_df: pd.DataFrame) -> None:
    read_write_benchmarks = benchmarks_df[
        (benchmarks_df.chunk_size.isin([64, 128]))
        & (~benchmarks_df.blosc_shuffle.isin(["noshuffle", "bitshuffle"]))
    ]

    create_read_write_plots_for_package(read_write_benchmarks, "zarr_python_2")
    create_read_write_plots_for_package(read_write_benchmarks, "zarr_python_3")
    create_read_write_plots_for_package(read_write_benchmarks, "tensorstore")

    read_chunks_128 = read_write_benchmarks[
        (read_write_benchmarks.group == "read")
        & (read_write_benchmarks.chunk_size == 128)
    ]
    write_chunks_128 = read_write_benchmarks[
        (read_write_benchmarks.group == "write")
        & (read_write_benchmarks.chunk_size == 128)
    ]

    plot_relplot_benchmarks(
        read_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        col="package",
        hue="compressor",
        size="compression_level",
        sub_dir_name="read",
        plot_name="all_packages",
    )

    plot_relplot_benchmarks(
        write_chunks_128,
        x_axis="stats.mean",
        y_axis="compression_ratio",
        col="package",
        hue="compressor",
        size="compression_level",
        sub_dir_name="write",
        plot_name="all_packages",
    )


def create_all_plots(json_ids: list[str] | None = None) -> None:
    """Create all plots. If json_ids aren't provided, process the latest benchmark results inside data/results.

    :param json_ids: optional list of json ids e.g. ["0001", "0002", "0003"] of the zarr-python-v2,
    zarr-python-v3 and tensorstore json to process.
    """
    result_path = Path(__file__).parents[2] / "data" / "results"
    sub_dirs = [sub_path for sub_path in result_path.iterdir() if sub_path.is_dir()]

    if len(sub_dirs) != 1:
        raise ValueError("Expected only one sub-directory inside data/results")
    result_path = sub_dirs[0]

    if json_ids is None:
        # Find the latest 3 json ids in the sub-dir
        all_ids = []
        for result_json in result_path.glob("*.json"):
            all_ids.append(result_json.stem.split("_")[0])

        json_ids = sorted(all_ids)[-3:]

    zarr_v2_path = result_path / f"{json_ids[0]}_zarr-python-v2.json"
    zarr_v3_path = result_path / f"{json_ids[1]}_zarr-python-v3.json"
    tensorstore_path = result_path / f"{json_ids[2]}_tensorstore.json"

    package_paths_dict = {
        "zarr_python_2": zarr_v2_path,
        "zarr_python_3": zarr_v3_path,
        "tensorstore": tensorstore_path,
    }

    benchmarks_df = get_benchmarks_dataframe(
        package_paths_dict,
    )

    create_read_write_plots(benchmarks_df)
    create_chunk_size_plots(benchmarks_df)
    create_shuffle_plots(benchmarks_df)

    print("Plotting finished 🕺")
    print("Plots saved to 'data/plots'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create plots from benchmark results. By default, processes the latest benchmark results from "
        "data/results. To override this, provide --json_ids."
    )
    parser.add_argument(
        "--json_ids",
        nargs=3,
        metavar="JSON_ID",
        help="provide the ids of the zarr-python-v2, zarr-python-v3 and tensorstore json files you want to process e.g. 0001 0002 0003",
    )
    args = parser.parse_args()

    create_all_plots(args.json_ids)
