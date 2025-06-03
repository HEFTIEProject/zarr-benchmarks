---
layout: default
---

# Zarr benchmarks

This page contains the results of a small project benchmarking the best options to use when creating Zarr arrays.
[Zarr](https://zarr.dev/) is a specification for storing array data, allowing efficient operations on them for huge datasets.

When you create a Zarr dataset, there are two important options you can set: the chunk shape, and the compression algorithm.
What choices to make isn't obvious, hence this project.

## Summary

- [tensorstore](https://google.github.io/tensorstore/) is faster than [Zarr-python 3](https://zarr.readthedocs.io/en/stable/) is faster than [Zarr-python 2](https://zarr.readthedocs.io/en/v2.18.5/).

All data we used for these tests is available at **put DOI here**.

### Dense image data

We used a **(shape)** shaped image with uint16 data type.

- Use Blosc with zstd, with a compression level of 9
- Use a compression level of 4 for quicker wrtie times but slightly smaller compression ratios (but similar read times).

### Dense label data

We used a **(shape)** shaped image with **dtype** data type.

- ...
- ...

### Sparse label data

## Compressors

### Write

![alt text](assets/write.png)

### Read

![alt text](assets/read.png)

### Shuffle

![alt text](assets/shuffle.png)

## Software libraries
