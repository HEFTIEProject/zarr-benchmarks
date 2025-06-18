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
tox -- --benchmark-only --image=heart --config=all --benchmark-storage=data/results/heart

# Run with a dense segmentation (small subset of C3 segmentation data from the H01 release)
tox -- --benchmark-only --image=dense --config=all --benchmark-storage=data/results/dense
```

This will run all benchmarks via `zarr-python` version 2 + 3 and `tensorstore`
with the given images. Each tox command will generate three result `.json` files
in the given `--benchmark-storage` directory - one for `zarr-python` version 2
(`{id}_zarr-python-v2.json`), one for `zarr-python` version 3
(`{id}_zarr-python-v3.json`) and one for tensorstore (`{id}_tensorstore.json`).
`{id}` is a four digit number (e.g. `0001`) that increments automatically for
every new `tox` run.

If `--benchmark-storage` isn't specified, json files will be saved to the
default `.benchmarks` directory. We recommend setting `--benchmark-storage` to
an appropriately named sub-directory within `data/results` (as in the example
above).

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
tox -- --benchmark-only --image=heart --config=shuffle --benchmark-storage=data/results/heart
```

### Specific package

To only run benchmarks for a specific package, use the `-e` option:

```bash
# tensorstore only
tox run -e py313-tensorstore -- --benchmark-only --image=heart --config=all --benchmark-storage=data/results/heart

# zarr-python v2 only
tox run -e py313-zarrv2 -- --benchmark-only --image=heart --config=all --benchmark-storage=data/results/heart

# zarr-python v3 only
tox run -e py313-zarrv3 -- --benchmark-only --image=heart --config=all --benchmark-storage=data/results/heart
```

To see a list of available environments, use `tox -l`.

### Options for quicker development runs

Removing the `--config` option will use a small `dev` config to test a small
selection of parameters:

```bash
tox -- --benchmark-only --image=heart --benchmark-storage=data/results/heart
```

You can also use a smaller image (128x128x128 numpy array) by using
`--image=dev` (this is also the default if no `--image` option is provided):

```bash
tox -- --benchmark-only --image=dev --benchmark-storage=data/results/dev
```

You can also override the default number of rounds / warmup rounds for each
benchmark with:

```bash
tox -- --benchmark-only --image=dev --rounds=1 --warmup-rounds=0 --benchmark-storage=data/results/dev
```

As described in the [specific package section](#specific-package), you can also
run with a single tox environment via e.g.:

```bash
tox run -e py313-tensorstore -- --benchmark-only --image=dev --benchmark-storage=data/results/dev
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

## Developer docs

Further information about code structure / implementation, is provided in the
[developer docs](DEVELOPERS.md).
