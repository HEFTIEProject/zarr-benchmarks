from datetime import datetime
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def load_benchmarks_json(path_to_file: Path) -> dict:
    with open(path_to_file, "r") as in_file_obj:
        text = in_file_obj.read()
        # convert the text into a dictionary
        return json.loads(text)


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
        ]
        + stats_cols
    ]
    benchmark_df = benchmark_df.rename(columns={"params.chunk_size": "chunk_size"})

    return benchmark_df


def get_benchmarks_dataframe(
    package_paths_dict: dict,
) -> pd.DataFrame:
    """Combine multiple pytest-benchmark json results into a single dataframe"""

    benchmark_dfs = []
    for id, json_path in package_paths_dict.items():
        benchmark_df = prepare_benchmarks_dataframe(load_benchmarks_json(json_path))
        benchmark_df.insert(0, "package", id)
        benchmark_dfs.append(benchmark_df)

    return pd.concat(benchmark_dfs, ignore_index=True)


def plot_relplot_subplots_benchmarks(
    data: pd.DataFrame,
    *,
    group: str,
    x_axis: str,
    y_axis: str,
    hue: str,
    path_to_file: str = None,
) -> None:
    graph = sns.relplot(
        data=data,
        x=x_axis,
        y=y_axis,
        col=hue,
        hue=hue,
        facet_kws=dict(sharex=False, sharey=False),
    )

    if x_axis.startswith("stats"):
        label = f"{x_axis.split('.')[-1]} {group} time (s)"
        graph.set_axis_labels(label, y_axis.capitalize().replace("_", " "))

    else:
        label = f"{y_axis.split('.')[-1]} {group} time (s)"
        graph.set_axis_labels(x_axis.capitalize().replace("_", " "), label)

    if path_to_file is not None:
        save_plot_as_png(
            graph,
            f"data/plots/{group}_subplot_relplot_{path_to_file[0]}.png",
        )


def plot_relplot_benchmarks(
    data: pd.DataFrame,
    *,
    group: str,
    x_axis: str,
    y_axis: str,
    hue: str,
    size: str,
    title: str,
    path_to_file: str = None,
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
    if x_axis.startswith("stats"):
        label = f"{x_axis.split('.')[-1]} {group} time (s)"
        graph.set_axis_labels(label, y_axis.capitalize().replace("_", " "))

    else:
        label = f"{y_axis.split('.')[-1]} {group} time (s)"
        graph.set_axis_labels(x_axis.capitalize().replace("_", " "), label)

    graph.figure.suptitle(title)
    graph.figure.subplots_adjust(top=0.9)

    if path_to_file is not None:
        save_plot_as_png(
            graph,
            f"data/plots/{group}_relplot_{path_to_file[0]}.png",
        )


def save_plot_as_png(plt: plt, path_to_file: str) -> None:
    plt.savefig(path_to_file, format="png", dpi=300)


if __name__ == "__main__":
    zarr_v2_path = "data/json/0007_zarr-python-v2.json"
    zarr_v3_path = "data/json/0008_zarr-python-v3.json"
    tensorstore_path = "data/json/0009_tensorstore.json"

    package_paths_dict = {
        "zarr_python_2": zarr_v2_path,
        "zarr_python_3": zarr_v3_path,
        "tensorstore": tensorstore_path,
    }

    benchmarks_df = get_benchmarks_dataframe(
        package_paths_dict,
    )
    benchmarks_zarr_v2 = benchmarks_df[benchmarks_df.package == "zarr_python_2"]
    write_zarr_v2 = benchmarks_zarr_v2[benchmarks_zarr_v2.group == "write"]
    read_zarr_v2 = benchmarks_zarr_v2[benchmarks_zarr_v2.group == "read"]

    write_zarr_v2_chunks_200 = write_zarr_v2[write_zarr_v2.chunk_size == 200]
    read_zarr_v2_chunks_200 = read_zarr_v2[read_zarr_v2.chunk_size == 200]

    benchmark_name = Path(zarr_v2_path).stem
    data = load_benchmarks_json(zarr_v2_path)
    machine_info = data["machine_info"]["machine"]
    date = datetime.now().strftime("%Y-%m-%d")

    path_to_file = [date + "_" + machine_info + "_" + benchmark_name]
    plot_relplot_benchmarks(
        write_zarr_v2_chunks_200,
        group="write",
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        title="zarr_python_2",
        path_to_file=path_to_file,
    )

    plot_relplot_benchmarks(
        read_zarr_v2_chunks_200,
        group="read",
        x_axis="stats.mean",
        y_axis="compression_ratio",
        hue="compressor",
        size="compression_level",
        title="zarr_python_2",
        path_to_file=path_to_file,
    )

    plot_relplot_subplots_benchmarks(
        write_zarr_v2_chunks_200,
        group="write",
        x_axis="stats.mean",
        y_axis="compression_level",
        hue="compressor",
        path_to_file=path_to_file,
    )
    plot_relplot_subplots_benchmarks(
        read_zarr_v2_chunks_200,
        group="read",
        x_axis="stats.mean",
        y_axis="compression_level",
        hue="compressor",
        path_to_file=path_to_file,
    )
