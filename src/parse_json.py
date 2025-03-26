import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def load_benchmarks_json(path_to_file: str) -> dict:
    with open(path_to_file, "r") as in_file_obj:
        text = in_file_obj.read()
        # convert the text into a dictionary
        return json.loads(text)


def prep_benchmarks_for_plotting(data, group, plot_type, path_to_file=None):
    compression_types = ["blosc", "gzip", "zstd"]
    plot_data = []
    counter = 0

    for benchmark in data["benchmarks"]:
        # Only prepare data in specified group
        if benchmark["group"] == group:
            counter += 1
            if plot_type == "scatter":
                stats = benchmark["stats"]["mean"]
            elif plot_type == "boxplot":
                stats = benchmark["stats"]["data"]
            else:
                raise ValueError(f"Unknown plot type: {plot_type}")

            params = benchmark["params"]
            compression_ratio = benchmark["extra_info"].get("compression_ratio", None)

            # Only prepare data for chunk size
            if params.get("chunk_size") == 100:
                if "blosc_clevel" in params:
                    compression_level = params["blosc_clevel"]
                    plot_data.append(
                        {
                            "write_time": stats,
                            "compression_ratio": compression_ratio,
                            "compression_type": compression_types[0],
                            "compression_level": compression_level,
                        }
                    )
                elif "gzip_level" in params:
                    compression_level = params["gzip_level"]
                    plot_data.append(
                        {
                            "write_time": stats,
                            "compression_ratio": compression_ratio,
                            "compression_type": compression_types[1],
                            "compression_level": compression_level,
                        }
                    )
                elif "zstd_level" in params:
                    compression_level = params["zstd_level"]
                    plot_data.append(
                        {
                            "write_time": stats,
                            "compression_ratio": compression_ratio,
                            "compression_type": compression_types[2],
                            "compression_level": compression_level,
                        }
                    )

    # Convert plot_data dataframe
    if plot_type == "boxplot":
        flattened_data = [
            {
                "write_time": time,
                "compression_ratio": entry["compression_ratio"],
                "compression_type": entry["compression_type"],
                "compression_level": entry["compression_level"],
            }
            for entry in plot_data
            for time in entry["write_time"]
        ]
        df = pd.DataFrame(flattened_data)
    elif plot_type == "scatter":
        df = pd.DataFrame(plot_data)

    # Generate a color palette dynamically for all unique compression levels
    unique_levels = df["compression_type"].unique()
    palette = sns.color_palette("husl", len(unique_levels))
    palette_dict = {level: color for level, color in zip(unique_levels, palette)}

    print("COUNTER = ", counter)

    if plot_type == "scatter":
        plot_benchmarks(df, group, plot_type, palette_dict, path_to_file)
    elif plot_type == "boxplot":
        plot_benchmarks(df, group, plot_type, palette_dict, path_to_file)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")


def plot_benchmarks(df, group, plot_type, palette_dict=None, path_to_file=None):
    x_label = group.capitalize() + " Time (s)"
    plt.clf()
    plt.figure(figsize=(10, 6))

    # Add labels and title
    plt.xlabel(x_label)
    plt.ylabel("Compression Ratio")
    plt.title(f"Compression Ratio vs {x_label} for Different Compression Types")

    if plot_type == "boxplot":
        sns.boxplot(
            x="write_time",
            y="compression_ratio",
            hue="compression_type",
            data=df,
            palette=palette_dict,
        )
    elif plot_type == "scatter":
        unique_types = df["compression_type"].unique()
        palette = sns.color_palette("husl", len(unique_types))
        palette_dict = {ctype: color for ctype, color in zip(unique_types, palette)}
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
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")

    save_plot_as_jpeg(
        plt,
        f"data/json/{group}_{plot_type}_{path_to_file.split('/')[2].split('.')[0]}.jpeg",
    )


def save_plot_as_jpeg(plt: plt, path_to_file: str) -> None:
    plt.savefig(path_to_file, format="jpeg", dpi=300)


if __name__ == "__main__":
    # path_to_file = "data/json/0008_small_img.json"
    path_to_file = "data/json/0003_zarr-python-v3.json"
    # path_to_file = "data/json/0002_zarr-python-v2.json"
    data = load_benchmarks_json(path_to_file)
    prep_benchmarks_for_plotting(data, "read", "scatter", path_to_file)
    prep_benchmarks_for_plotting(data, "write", "scatter", path_to_file)

    machine_info = data["machine_info"]["cpu"]
