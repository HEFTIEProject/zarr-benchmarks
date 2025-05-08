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
    title: str,
    size: str | None = None,
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
            Path(__file__).parents[2]
            / "data"
            / "plots"
            / f"{group}_relplot_{output_filename}.png",
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
        col_wrap=3,
    )

    x_axis_label, y_axis_label = get_axis_labels(x_axis, y_axis, group)
    graph.set_axis_labels(x_axis_label, y_axis_label)

    if output_filename is not None:
        save_plot_as_png(
            graph,
            Path(__file__).parents[2]
            / "data"
            / "plots"
            / f"{group}_subplot_relplot_{output_filename}.png",
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


def save_plot_as_png(grid: sns.FacetGrid, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    grid.savefig(output_path, format="png", dpi=300)


def create_shuffle_plots(
    benchmarks_df: pd.DataFrame,
) -> None:
    shuffle_benchmarks = benchmarks_df[
        (benchmarks_df.compressor == "blosc-zstd")
        & (benchmarks_df.compression_level == 3)
        & (benchmarks_df.chunk_size == 128)
    ]

    graph = sns.catplot(
        data=shuffle_benchmarks,
        x="blosc_shuffle",
        y="compression_ratio",
        hue="package",
        kind="bar",
        height=4,
        aspect=1.5,
    )

    save_plot_as_png(
        graph,
        Path(__file__).parents[2]
        / "data"
        / "plots"
        / "blosc_shuffle_compression_ratio.png",
    )

    write = shuffle_benchmarks[shuffle_benchmarks.group == "write"]

    graph = sns.catplot(
        data=write,
        x="blosc_shuffle",
        y="stats.mean",
        hue="package",
        kind="bar",
        height=4,
        aspect=1.5,
    )

    save_plot_as_png(
        graph,
        Path(__file__).parents[2] / "data" / "plots" / "blosc_shuffle_write.png",
    )

    read = shuffle_benchmarks[shuffle_benchmarks.group == "read"]

    graph = sns.catplot(
        data=read,
        x="blosc_shuffle",
        y="stats.mean",
        hue="package",
        kind="bar",
        height=4,
        aspect=1.5,
    )

    save_plot_as_png(
        graph,
        Path(__file__).parents[2] / "data" / "plots" / "blosc_shuffle_read.png",
    )


def create_chunk_size_plots(
    benchmarks_df: pd.DataFrame,
) -> None:
    chunk_size_benchmarks = benchmarks_df[
        (benchmarks_df.compressor == "blosc-zstd")
        & (benchmarks_df.compression_level == 3)
        & (benchmarks_df.blosc_shuffle == "shuffle")
    ]

    # pdb.set_trace()

    plot_relplot_subplots_benchmarks(
        chunk_size_benchmarks,
        group="write",
        x_axis="chunk_size",
        y_axis="compression_ratio",
        hue="package",
        output_filename="chunk_size_compression_ratio",
    )

    chunk_size_write = chunk_size_benchmarks[chunk_size_benchmarks.group == "write"]

    plot_relplot_subplots_benchmarks(
        chunk_size_write,
        group="write",
        y_axis="stats.mean",
        x_axis="chunk_size",
        hue="package",
        output_filename="chunk_size_write",
    )

    plot_relplot_benchmarks(
        chunk_size_write,
        group="write",
        y_axis="stats.mean",
        x_axis="chunk_size",
        hue="package",
        title="chunk_size_write_all",
        output_filename="chunk_size_write_all",
    )

    chunk_size_read = chunk_size_benchmarks[chunk_size_benchmarks.group == "read"]

    plot_relplot_subplots_benchmarks(
        chunk_size_read,
        group="read",
        y_axis="stats.mean",
        x_axis="chunk_size",
        hue="package",
        output_filename="chunk_size_read",
    )

    plot_relplot_benchmarks(
        chunk_size_read,
        group="read",
        y_axis="stats.mean",
        x_axis="chunk_size",
        hue="package",
        title="chunk_size_read_all",
        output_filename="chunk_size_read_all",
    )


def create_read_write_plots(
    benchmarks_df: pd.DataFrame,
    zarr_v2_path: str,
) -> None:
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

    # create_read_write_plots(benchmarks_df, zarr_v2_path)
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
