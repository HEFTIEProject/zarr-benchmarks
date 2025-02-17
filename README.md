# Zarr benchmarks for 3D images

This repository contains benchmarks for creating, reading, and storing huge 3D images in [Zarr](https://zarr.dev/) arrays.
It is one part of the [HEFTIE project](https://github.com/HEFTIEProject).

## Other related work

- [`zarr-developers/zarr-benchmark`](https://github.com/zarr-developers/zarr-benchmark)
- [`LDeakin/zarr_benchmarks`](https://github.com/LDeakin/zarr_benchmarks)

## Project plan

The goal of this task is to benchmark writing data to Zarr with a range of different _configurations_ (e.g., compression codec, chunk size...), to guide the choice of options for folks reading and writing 3D imaging data.
We will do this with the following considerations:

- Benchmarks should be easy to run on a typical laptop. This means:
  - **small test data** (< 1GB)
  - **quick** (~seconds for individual benchmarks, ~minutes for the whole set of benchmarks)
- Benchmarks will be run on spatial **3D imaging data**, and **segmenations** of that data
- The most important measurement to make is compression ratio - data will sit on disks unchanged for years, but performance of the libraries to read/write the data can improve on much shorter timescales.

### Data

To start with, we will use a downsampled version of a full organ dataset from the [Human Organ Atalas](https://human-organ-atlas.esrf.fr) (for example [this heart dataset](https://human-organ-atlas.esrf.fr/datasets/1773966096) )

### Measurements

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
  - To limit options, use only [codecs supported by neuroglancer](https://github.com/google/neuroglancer/tree/master/src/datasource/zarr#zarr-v2) for both Zarr v2 and Zarr v3: `blosc`, `gzip`, `zstd`
- Compression codec parameters, e.g., compression level
- Chunk size
  - To keep things simple, use a isotropic chunk shape (e.g., (128, 128, 128)) and just vary the chunk size.
- Shard size (only for Zarr format 3)
- Type of data
  - Imaging data
  - "Sparse" segmentation data (e.g., arteries)
  - "Dense" segmentation data (e.g., cells)

### Stretch goals

- Run benchmarks using `zarr-python` version 3 and/or `tensorstore`
- Run benchmarks using `zarr-python` version 3 and [`zarrs-python`](https://github.com/ilan-gold/zarrs-python)
- Try different sharding options in Zarr format 3
