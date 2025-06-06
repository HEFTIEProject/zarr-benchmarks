from datetime import datetime
from pathlib import Path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def get_limits_custom(x_min: int, x_max: int, max_range: int) -> tuple[float, float]:
    central_value = (x_min + x_max) / 2
    x_lim_min = central_value - max_range / 2 - round(max_range, 1) / 10
    x_lim_max = central_value + max_range / 2 + round(max_range, 1) / 10
    return x_lim_min, x_lim_max


def set_axes_limits(graph: sns.relplot, data: pd.DataFrame, plot_name: str) -> None:
    """Set all subplots to cover the same total x axis range (= max_range across all subplots),
    centred on their central x value.
    """

    compressors = {}
    for compressor, ax in graph.axes_dict.items():
        # Filter data for this compressor
        compressor_data = data[data.compressor == compressor]

        # Get max / min x values for this compressor - bearing in mind we're plotting the mean with
        # errorbars of length 2* standard deviation
        x_min = (
            compressor_data["stats.mean"] - 2 * compressor_data["stats.stddev"]
        ).min()
        x_max = (
            compressor_data["stats.mean"] + 2 * compressor_data["stats.stddev"]
        ).max()

        compressors[compressor] = {
            "x_min": x_min,
            "x_max": x_max,
            "range": x_max - x_min,
        }

    max_range = max([compressors[compressor]["range"] for compressor in compressors])

    for compressor, ax in graph.axes_dict.items():
        # Set the x-axis limits for each subplot
        compressor = compressors[compressor]
        x_lim_min, x_lim_max = get_limits_custom(
            compressor["x_min"], compressor["x_max"], max_range
        )
        ax.set_xlim(x_lim_min, x_lim_max)


def plot_errorbars_benchmarks(
    data: pd.DataFrame,
    *,
    sub_dir_name: str,
    plot_name: str,
    title: str | None = None,
    hue: str | None = None,
    size: str | None = None,
    col: str | None = None,
) -> None:
    """Generate a scatter plot including errorbars using seaborn's relplot function with a dataframe as input.
    Calls a function to save the plot as a PNG file.

    Args:
        data (pd.DataFrame): Contains the data to be plotted.
        sub_dir_name (str): name of the sub-directory where the plot will be saved within data/plots
        plot_name (str): name of the plot which will be used for the start of the final filename
        title (str | None, optional): title of the plot. Defaults to None.
        hue (str | None, optional): name of dataframe column to be used for the colours in the plot. Defaults to None.
        size (str | None, optional): name of dataframe column to be used for size of datapoints. Defaults to None.
        col (str | None, optional): name of dataframe column to be used for splitting into subplots. Defaults to None.
    """
    x_axis = "stats.mean"
    y_axis = "compression_ratio"
    if col is None:
        facet_kws = None
        col_wrap = None
        plot_name = plot_name
    else:
        facet_kws = dict(sharex=False, sharey=False)
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
        size=size,
        col=col,
        height=4,
        aspect=1.5,
        facet_kws=facet_kws,
        col_wrap=col_wrap,
    )

    # Add error bars using matplotlib
    def add_error_bars(x, y, x_stddev, **kwargs):
        ax = plt.gca()
        ax.errorbar(x, y, xerr=2 * x_stddev, fmt="none", **kwargs)

    graph.map(add_error_bars, x_axis, y_axis, "stats.stddev")

    set_axes_limits(graph, data, plot_name)

    x_axis_label, y_axis_label = get_axis_labels(data, x_axis=x_axis, y_axis=y_axis)

    graph.set_axis_labels(x_axis_label, y_axis_label)

    if title is not None:
        title = title + " - 2 standard deviations errorbars"
        graph.figure.suptitle(title)
        graph.tight_layout()

    save_plot_as_png(
        graph,
        get_output_path(data, sub_dir_name, plot_name),
    )


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
