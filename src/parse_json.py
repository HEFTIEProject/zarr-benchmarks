import json
import pdb
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

def plot_benchmarks(df, x_label, plot_type, palette_dict=None):
    # Plot using seaborn
    plt.figure(figsize=(10, 6))
     # Add labels and title
    plt.xlabel(x_label)
    plt.ylabel("Compression Ratio")
    plt.title(f"Compression Ratio vs {x_label} for Different Compression Types")
    plt.legend(title="Compression Level")
    if plot_type == "boxplot":
        sns.boxplot(
        x="write_time",
        y="compression_ratio",
        hue="compression_type",
        data=df[0:81],
        palette=palette_dict
    )
    elif plot_type == "scatter":
        sns.scatterplot(
        data=df,
        x="write_time",
        y="compression_ratio",
        hue="compression_type",
        style="compression_level",
        palette=palette_dict,
        s=100  # Size of the scatter points
    )
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")
    
   
    
    save_plot_as_jpeg(plt, f"data/json/{plot_type}.jpeg")
    

def plot_compression_benchmarks(data, plot_type):
    # Prepare data for plotting
    compression_types = ["blosc", "gzip", "zstd"]
    plot_data = []

    for benchmark in data["benchmarks"]:
        if plot_type == "scatter":
            stats = benchmark["stats"]["mean"]
        elif plot_type == "boxplot":
            stats = benchmark["stats"]["data"]
        else:
            raise ValueError(f"Unknown plot type: {plot_type}")
        
        params = benchmark["params"]
        compression_ratio = benchmark["extra_info"].get("compression_ratio", None)

        # Determine compression type and level
        for compression in compression_types:
            if params.get("chunk_size") == 300:
                
                if "blosc_clevel" in params:
                    compression_level = params["blosc_clevel"]
                    plot_data.append({
                        "write_time": stats,  # Assuming stats is a list of write times
                        "compression_ratio": compression_ratio,
                        "compression_type": compression,
                        "compression_level": compression_level
                    })
                elif "gzip_level" in params:
                    compression_level = params["gzip_level"]
                    plot_data.append({
                        "write_time": stats,  # Assuming stats is a list of write times
                        "compression_ratio": compression_ratio,
                        "compression_type": compression,
                        "compression_level": compression_level
                    })
                elif "zstd_level" in params:
                    compression_level = params["zstd_level"]
                    plot_data.append({
                        "write_time": stats,  # Assuming stats is a list of write times
                        "compression_ratio": compression_ratio,
                        "compression_type": compression,
                        "compression_level": compression_level
                    })

    # Convert plot_data into a format suitable for seaborn
    if plot_type == "boxplot":
        flattened_data = [
            {
                "write_time": time,
                "compression_ratio": entry["compression_ratio"],
                "compression_type": entry["compression_type"],
                "compression_level": entry["compression_level"]
            }
            for entry in plot_data
            for time in entry["write_time"]
        ]
        df = pd.DataFrame(flattened_data)
    elif plot_type == "scatter":
        df = pd.DataFrame(plot_data)

    
    # pdb.set_trace()
    # Generate a color palette dynamically for all unique compression levels
    unique_levels = df["compression_type"].unique()
    palette = sns.color_palette("husl", len(unique_levels))  # Generate distinct colors
    palette_dict = {level: color for level, color in zip(unique_levels, palette)}
    
    if plot_type == "scatter":
        plot_benchmarks(df, "Write Time", "scatter", palette_dict)
    elif plot_type == "boxplot":    
        plot_benchmarks(df, "Write Time", "boxplot", palette_dict)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")


    


def load_benchmarks_json(path_to_file: str) -> dict:
    with open(path_to_file, "r") as in_file_obj:
        text = in_file_obj.read()
        # convert the text into a dictionary
        return json.loads(text)
    
def plot_benchmark(data: dict) -> plt:
    # Create the box plot
    plt.clf()
    plt.boxplot(data, vert=True, patch_artist=True, showmeans=True)
    # pdb.set_trace()
    # Add labels and title
    plt.title("Whisker Plot (Box Plot) Example")
    plt.ylabel("Values")
    return plt


def save_plot_as_jpeg(plt: plt, path_to_file: str) -> None:
    plt.savefig(path_to_file, format="jpeg", dpi=300)

if __name__ == "__main__":
    path_to_file = "data/json/0008_small_img.json"
    data = load_benchmarks_json(path_to_file)
    plot_compression_benchmarks(data, "scatter")
    plot_compression_benchmarks(data, "boxplot")
    
    for benchmark in range(len(data["benchmarks"])):
        print("Benchmark: ", benchmark)
        print(data["benchmarks"][benchmark]["stats"]["data"])
        plot = plot_benchmark(data["benchmarks"][benchmark]["stats"]["data"])
        # if benchmark > 7:
        #     save_plot_as_jpeg(plot, f"data/json/{benchmark}.jpeg")
    
    machine_info = data["machine_info"]["cpu"]
    for benchmark in range(len(data["benchmarks"])):
        # print(data["benchmarks"][benchmark]["group"])
        # print(data["benchmarks"][benchmark]["name"])
        # print(data["benchmarks"][benchmark]["stats"]["data"])
        # print(
        #     data["benchmarks"][benchmark]["extra_info"]["compression_ratio"]
        #     if "compression_ratio" in data["benchmarks"][benchmark]["extra_info"]
        #     else None
        # )
        if data["benchmarks"][benchmark]["group"]=='read':
            print(data["benchmarks"][benchmark]["params"]["chunk_size"])
            print('hey', benchmark)
            print(
                data["benchmarks"][benchmark]["params"].get("blosc_clevel")
                or data["benchmarks"][benchmark]["params"].get("gzip_level")
                or data["benchmarks"][benchmark]["params"].get("zstd_level")
            )
            print('bye')
