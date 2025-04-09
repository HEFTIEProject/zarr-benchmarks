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
    json_paths: tuple[Path], package_ids: tuple[str]
) -> pd.DataFrame:
    """Combine multiple pytest-benchmark json results into a single dataframe"""

    benchmark_dfs = []
    for json_path, id in zip(json_paths, package_ids):
        benchmark_df = prepare_benchmarks_dataframe(load_benchmarks_json(json_path))
        benchmark_df.insert(0, "package", id)
        benchmark_dfs.append(benchmark_df)

    return pd.concat(benchmark_dfs, ignore_index=True)


def plot_scatter_benchmarks(
    df: pd.DataFrame, group: str, palette_dict=None, path_to_file=None
):
    x_label = group.capitalize() + " Time (s)"
    plt.clf()
    plt.figure(figsize=(10, 6))

    # Add labels and title
    plt.xlabel(x_label)
    plt.ylabel("Compression Ratio")
    plt.title(f"Compression Ratio vs {x_label} for Different Compression Types")

    sns.scatterplot(
        data=df,
        x="write_time",
        y="compression_ratio",
        hue="compression_type",
        style="compression_level",
        alpha=0.7,
        palette=palette_dict,
        s=100,
    )

    save_plot_as_png(
        plt,
        f"data/json/{group}_scatter_{Path(path_to_file).stem}.png",
    )


def plot_errorbars_benchmarks(df, group, palette_dict=None, path_to_file=None):
    x_label = group.capitalize() + " Time (s)"
    plt.clf()
    plt.figure(figsize=(10, 6))

    # Add labels and title
    plt.xlabel(x_label)
    plt.ylabel("Compression Ratio")
    plt.title(f"Compression Ratio vs {x_label} for Different Compression Types")

    sns.boxplot(
        x="write_time",
        y="compression_ratio",
        hue="compression_type",
        data=df,
        palette=palette_dict,
    )

    save_plot_as_png(
        plt,
        f"data/json/{group}_errorbars_{Path(path_to_file).stem}.png",
    )


def plot_relplot_benchmarks(data: pd.DataFrame, group: str, path_to_file=None):
    graph = sns.relplot(
        data=data,
        x="stats.mean",
        y="compression_ratio",
        hue="compressor",
        style="compressor",
        size="compression_level",
        height=4,
        aspect=1.5,
    )
    graph.set_axis_labels("Mean write time (s)", "Compression ratio")

    if path_to_file is not None:
        save_plot_as_png(
            graph,
            f"data/json/{group}_errorbars_{Path(path_to_file).stem}.png",
        )


def save_plot_as_png(plt: plt, path_to_file: str) -> None:
    plt.savefig(path_to_file, format="png", dpi=300)


if __name__ == "__main__":
    zarr_v2_path = "data/json/0007_zarr-python-v2.json"
    zarr_v3_path = "data/json/0008_zarr-python-v3.json"
    tensorstore_path = "data/json/0009_tensorstore.json"

    benchmarks_df = get_benchmarks_dataframe(
        (zarr_v2_path, zarr_v3_path, tensorstore_path),
        package_ids=("zarr_python_2", "zarr_python_3", "tensorstore"),
    )
    benchmarks_zarr_v2 = benchmarks_df[benchmarks_df.package == "zarr_python_2"]
    write_zarr_v2 = benchmarks_zarr_v2[benchmarks_zarr_v2.group == "write"]
    read_zarr_v2 = benchmarks_zarr_v2[benchmarks_zarr_v2.group == "read"]

    write_zarr_v2_chunks_200 = write_zarr_v2[write_zarr_v2.chunk_size == 200]
    read_zarr_v2_chunks_200 = read_zarr_v2[read_zarr_v2.chunk_size == 200]

    plot_relplot_benchmarks(write_zarr_v2_chunks_200, "write", zarr_v2_path)
    plot_relplot_benchmarks(read_zarr_v2_chunks_200, "read", zarr_v2_path)

    data = load_benchmarks_json(zarr_v2_path)
    machine_info = data["machine_info"]["cpu"]
