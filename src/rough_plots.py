import json
import pandas as pd
from pathlib import Path


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
            "params.blosc_shuffle"
        ]
        + stats_cols
    ]
    benchmark_df = benchmark_df.rename(columns={"params.chunk_size": "chunk_size", "params.blosc_shuffle": "blosc_shuffle"})

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


if __name__ == "__main__":
    zarr_v2_path = "data/json/0007_zarr-python-v2.json"
    zarr_v3_path = "data/json/0008_zarr-python-v3.json"
    tensorstore_path = "data/json/0009_tensorstore.json"

    benchmarks_df = get_benchmarks_dataframe(
        (zarr_v2_path, zarr_v3_path, tensorstore_path),
        package_ids=("zarr_python_2", "zarr_python_3", "tensorstore"),
    )
