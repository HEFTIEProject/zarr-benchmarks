# Developer documentation

This file describes the structure of the `zarr-benchmarks` codebase and explains
key parts of its implementation.

## Benchmark libraries

### pytest-benchmark / pytest

[`pytest-benchmark`](https://pytest-benchmark.readthedocs.io/en/latest/) is a
plugin for [`pytest`](https://docs.pytest.org/en/stable/), that provides a
`benchmark` fixture.

Tests using this fixture can run a section of code multiple times, and output
summary statistics for run time like `min`, `max`, `mean` and
`standard deviation` to the `pytest` terminal output, or to a separate JSON
file.

This fixture has a
[`pedantic` mode](https://pytest-benchmark.readthedocs.io/en/latest/pedantic.html)
that provides extra control over how benchmarks are run. We use this mode
throughout, to allow use of a `setup` function that removes generated Zarr
images between benchmark runs.

Every benchmark is run a certain number of times (`rounds`) to calculate the
summary statistics. There are also `warmup_rounds` (run before `rounds`), that
aren't included in the statistics.

### Running the benchmarks

We use `tox` to enable testing with different Zarr libraries and versions. We
test:

- [`zarr-python`](https://zarr.readthedocs.io/en/stable/) version 2
- [`zarr-python`](https://zarr.readthedocs.io/en/stable/) version 3
- [`tensorstore`](https://google.github.io/tensorstore/)

Each is installed in a separate `tox` environment, where the benchmarks are run
via calls to `pytest`.

### Fetching / caching test data

Images for benchmarking are fetched automatically from Zenodo using `pooch`.
This stores files in a local cache, and only re-downloads data if it has been
changed on Zenodo.

## Benchmark code structure

### Benchmarks

Each benchmark is structured as a `pytest` test under `tests/benchmarks`.
Benchmarks for read time are in `test_read_zarr_benchmark.py` and write time in
`test_write_zarr_benchmark.py`. All benchmarks write temporary Zarr images to
`data/output`, that are removed between runs.

Each of these benchmarks runs in all three tox environments i.e. with
`zarr python v2`, `zarr python v3` and `tensorstore`.

### Helper code

All the code for reading / writing Zarr images, as well as fetching datasets and
making plots is stored under `src/zarr_benchmarks`.

The read/write code for each Zarr library is stored under
`src/zarr_benchmarks/read_write_zarr`. To reduce the amount of boilerplate
needed to run benchmarks, the files for each library (ie.
`read_write_tensorstore`, `read_write_zarr_python_v2` and
`read_write_zarr_python_v3`) provide functions with the same names and
parameters. The `__init__` file of this module provides an alias,
`read_write_zarr`, that will refer to the correct file depending on which
library is installed in the current tox environment.

This allows each benchmark to be written once (rather than having separate
versions for each library), by using:

```python
from zarr_benchmarks.read_write_zarr import read_write_zarr

# Then use the functions that have the same name / parameters across all files e.g.
read_write_zarr.get_blosc_compressor(blosc_cname, blosc_clevel, blosc_shuffle)
```

### Tests

Some tests are provided under `tests/tests`. These are standard `pytest` tests,
that don't use the `benchmark` fixture from `pytest-benchmark`. As with the rest
of the code, they will be run in all tox environments.

If a test should only be run in the `tensorstore` env, mark it with:

```python
pytestmark = [pytest.mark.tensorstore]
```

If a test should only be run in `zarr-python` envs (v2 + v3), mark it with:

```python
pytestmark = [pytest.mark.zarr_python]
```

## Command-line options

Additional `pytest` commandline options e.g. for setting the number of rounds /
warmup rounds, are configured in `tests/conftest.py` via the `pytest_addoption`
function.

Note that `pytest-benchmark` also has
[various commandline options](https://pytest-benchmark.readthedocs.io/en/latest/usage.html#commandline-options)
that can be used e.g. `--benchmark-storage` / `--benchmark-only`.

## Parameters / config

### Config files

The benchmarks test various combinations of Zarr settings e.g.:

- chunk size
- compression level
- type of compressor...

The combination of Zarr settings to use are set via `.json` config files under
`tests/benchmarks/benchmark_configs`. A description of all config values, as
well as their allowed values / ranges, is provided by a
['json schema'](https://json-schema.org/):
`tests/benchmarks/benchmark_configs/schema`. This schema is also used for
automatic validation of config `.jsons`.

Each config setting (e.g. `chunk_size`) corresponds to a parameter used in
benchmark functions under `tests/benchmarks`. Values set in the config e.g.
`"chunk_size": [64, 128]` will set the values of the corresponding parameter -
so a benchmark function with `chunk_size` as a parameter, will be run for both
`chunk_size = 64` and `chunk_size = 128`.

### Parameter combinations

Bear in mind that the number of combinations can quickly escalate! For example,
the read/write benchmarks for the `blosc` compressor have the following config
options: `chunk_size`, `blosc_clevel`, `blosc_shuffle` and `blosc_cname`. Values
for each of these parameters will be combined all for all so e.g.

```JSON
# blosc config file options

"chunk_size": [64, 128],
"blosc_clevel": [3, 4],
"blosc_shuffle": ["shuffle"],
"blosc_cname": ["blosclz", "lz4"],
```

will result in the benchmark function being run with the following 8
combinations:

| Chunk size | Blosc clevel | Blosc shuffle | Blosc cname |
| :--------- | :----------- | :------------ | :---------- |
| 64         | 3            | "shuffle"     | "blosclz"   |
| 64         | 3            | "shuffle"     | "lz4"       |
| 64         | 4            | "shuffle"     | "blosclz"   |
| 64         | 4            | "shuffle"     | "lz4"       |
| 128        | 3            | "shuffle"     | "blosclz"   |
| 128        | 3            | "shuffle"     | "lz4"       |
| 128        | 4            | "shuffle"     | "blosclz"   |
| 128        | 4            | "shuffle"     | "lz4"       |

If you only want to run certain combinations of parameters, they can be split
into multiple `config` files. For example, we have a `chunk_size` config file to
benchmark all chunk sizes from 60-130 with one specific compressor. By keeping
this in its own config file, we avoid creating combinations of many chunk sizes
with gzip / zstd / other blosc compressors that we don't need.

### Config parsing

Parsing of config files is handled in `tests/conftest.py` via the
`pytest_generate_tests` function. This is a
[built-in `pytest` function](https://docs.pytest.org/en/stable/how-to/parametrize.html#pytest-generate-tests)
that is called once per test function during the collection phase.

Here, specific config files are parsed (or multiple with `config=all`),
combinations of parameters are generated, then set on the relevant functions
with `metafunc.parametrize()`. This is equivalent to adding
`@pytest.mark.parametrize()` for each function, but parameters are being set
dynamically at run-time based on the contents of the config files.
