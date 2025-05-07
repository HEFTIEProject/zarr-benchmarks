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

### All benchmarks

Install the relevant dependencies with:

```bash
# Run from the top level of this repository
pip install .
```

Then run tox with:

```bash
tox -- --benchmark-only --config=all
```

This will run all benchmarks via `zarr-python` version 2 + 3 and `tensorstore`
with the example Human Organ Atlas image. All results will be saved as `.json`
files to the `data/results` directory.

### Specific config

`--config=all` will use parameters from all configuration files under
`tests/benchmarks/benchmark_configs` (except for `dev` which contains a small
selection of parameters for quick test runs). To run with parameters from a
single config file use e.g.

```bash
tox -- --benchmark-only --config=shuffle
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
tox -- --benchmark-only
```

You can also use a smaller image (100x100x100 numpy array) by adding
`--dev-image`:

```bash
tox -- --benchmark-only --dev-image
```

You can also override the default number of rounds / warmup rounds for each
benchmark with:

```bash
tox -- --benchmark-only --dev-image --rounds=1 --warmup-rounds=0
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
python src/zarr_benchmarks/parse_json_for_plots.py
```

This will process the latest benchmark results from `data/results` and create
plots as .png files under `data/plots`. If you want to process older benchmark
results, you can explicitly provide the ids of the `zarr-python-v2`,
`zarr-python-v2` and `tensorstore` jsons:

```bash
python src/zarr_benchmarks/parse_json_for_plots.py --json_ids 0001 002 0003
```

To see more info about what these values represent run:

```bash
python src/zarr_benchmarks/parse_json_for_plots.py -h
```

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
