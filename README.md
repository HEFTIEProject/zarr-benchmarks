# Zarr benchmarks for 3D images

This repository contains benchmarks for creating, reading, and storing huge 3D
images in [Zarr](https://zarr.dev/) arrays. It is one part of the
[HEFTIE project](https://github.com/HEFTIEProject).

The goal of this repository is to benchmark writing data to Zarr with a range of
different _configurations_ (e.g., compression codec, chunk size...), to guide
the choice of options for folks reading and writing 3D imaging data.

## Other related work

- [`zarr-developers/zarr-benchmark`](https://github.com/zarr-developers/zarr-benchmark)
- [`LDeakin/zarr_benchmarks`](https://github.com/LDeakin/zarr_benchmarks)
- [Zarr Visualization Report](https://nasa-impact.github.io/zarr-visualization-report/)
- [`icechunk` benchmarks](https://github.com/earth-mover/icechunk/tree/main/icechunk-python/notebooks/performance)

## Running the benchmarks

### Installation

Install the relevant dependencies with:

```bash
# Run from the top level of this repository
pip install -e .[plots]
```

If using `uv`, you can also install the dependencies with:

```bash
uv pip install -e ".[plots]"
```

Note: there are a number of optional dependencies that can be installed, if
required. See the [development dependencies](#development-dependencies) section.

### All benchmarks

To run all benchmarks (with all images) run the following tox commands:

```bash
# Run with an image of a heart from the Human Organ Atlas
tox -- --benchmark-only --image=heart --config=all

# Run with a dense segmentation (small subset of C3 segmentation data from the H01 release)
tox -- --benchmark-only --image=dense --config=all
```

This will run all benchmarks via `zarr-python` version 2 + 3 and `tensorstore`
with the given images. Each tox command will generate three result `.json` files
in the `data/results` directory - one for `zarr-python` version 2
(`{id}_zarr-python-v2.json`), one for `zarr-python` version 3
(`{id}_zarr-python-v3.json`) and one for tensorstore (`{id}_tensorstore.json`).
`{id}` is a four digit number (e.g. `0001`) that increments automatically for
every new `tox` run.

Note: the first time these commands are run, the required datasets will be
downloaded from
[HEFTIE's Zenodo repository](https://doi.org/10.5281/zenodo.15544055) and cached
locally on your computer. Later runs will re-use this data, and should be
faster. Information about the source of these datasets is provided in the
`LICENSE` file within each `.zarr` file on Zenodo.

### Specific config

`--config=all` will use parameters from all configuration files under
`tests/benchmarks/benchmark_configs` (except for `dev` which contains a small
selection of parameters for quick test runs). To run with parameters from a
single config file use e.g.

```bash
tox -- --benchmark-only --image=heart --config=shuffle
```

### Specific package

To only run benchmarks for a specific package, use the `-e` option:

```bash
# tensorstore only
tox run -e py313-tensorstore

# zarr-python v2 only
tox run -e py313-zarrv2

# zarr-python v3 only
tox run -e py313-zarrv3
```

To see a list of available environments, use `tox -l`.

### Options for quicker development runs

Removing the `--config` option will use a small `dev` config to test a small
selection of parameters:

```bash
tox -- --benchmark-only --image=heart
```

You can also use a smaller image (128x128x128 numpy array) by using
`--image=dev` (this is also the default if no `--image` option is provided):

```bash
tox -- --benchmark-only --image=dev
```

You can also override the default number of rounds / warmup rounds for each
benchmark with:

```bash
tox -- --benchmark-only --image=dev --rounds=1 --warmup-rounds=0
```

Everything after the first `--` will be passed to the internal `pytest` call, so
you can add any pytest options you require.

## Running the tests

Running `tox` without `--benchmark-only`, will run the tests + the benchmarks.
To only run the tests use:

```bash
tox -- --benchmark-skip
```

## Creating plots

Once in your virtual environment, you can create plots with:

```bash
python src/zarr_benchmarks/create_plots.py
```

This will process the latest benchmark results from `data/results` and create
plots as .png files under `data/plots`. If you want to process older benchmark
results, you can explicitly provide the ids of the `zarr-python-v2`,
`zarr-python-v3` and `tensorstore` jsons:

```bash
python src/zarr_benchmarks/create_plots.py --json_ids 0001 002 0003
```

To see more info about what these values represent and additional options run:

```bash
python src/zarr_benchmarks/create_plots.py -h
```

## Development dependencies

If required, you can install all tensorstore + zarr-python dependencies with:

```bash
pip install .[plots,tensorstore,zarr-python-v3]
```

Use `zarr-python-v2` if you need version 2 instead.

## Running pre-commit locally

If you want quick development, you can always do git commit -n which will
disable the check (but still run in CI). Or don’t run pre-commit install until
you need it.

## Project considerations

- Benchmarks should be easy to run on a typical laptop. This means:
  - **small test data** (< 1GB)
  - **quick** (~seconds for individual benchmarks, ~minutes for the whole set of
    benchmarks)
- Benchmarks will be run on spatial **3D imaging data**, and **segmenations** of
  that data
- The most important measurement to make is compression ratio - data will sit on
  disks unchanged for years, but performance of the libraries to read/write the
  data can improve on much shorter timescales.
- The most important software and configurations to test are those that are
  mature, reliable, and usable _now_ by a wide range of scientists.

### Data

To start with, we will use a downsampled version of a full organ dataset from
the [Human Organ Atalas](https://human-organ-atlas.esrf.fr) (for example
[this heart dataset](https://human-organ-atlas.esrf.fr/datasets/1773966096) )

### Measurements

For each configuration we will record:

1. Write time
2. Read time
3. Compression ratio

### Configurations

When benchmarking we will vary:

- Zarr implementation
  - `zarr-python` v2, `zarr-python` v3, and `tensorstore`
- Zarr data format version
  - 2 and 3
- Compression codec
  - To limit options, use only
    [codecs supported by neuroglancer](https://github.com/google/neuroglancer/tree/master/src/datasource/zarr#zarr-v2)
    for both Zarr v2 and Zarr v3: `blosc`, `gzip`, `zstd`
- Compression codec parameters, e.g., compression level
- Chunk size
  - To keep things simple, use a isotropic chunk shape (e.g., (128, 128, 128))
    and just vary the chunk size.
- Shard size (only for Zarr format 3)
- Type of data
  - Imaging data
  - "Sparse" segmentation data (e.g., arteries)
  - "Dense" segmentation data (e.g., cells)

### Stretch goals

- Run benchmarks using `zarr-python` version 3 and/or `tensorstore`
- Run benchmarks using `zarr-python` version 3 and
  [`zarrs-python`](https://github.com/ilan-gold/zarrs-python)
- Try different sharding options in Zarr format 3
