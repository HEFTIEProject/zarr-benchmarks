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

## Configuration

### Dense image data

We used a **(shape)** shaped image with uint16 data type.

- Use Blosc with zstd, with a compression level of 9
- Use a compression level of 4 for quicker wrtie times but slightly smaller compression ratios (but similar read times).

### Dense label data

We used a **(shape)** shaped image with **dtype** data type.

- ...
- ...

### Sparse label data

### Default configuration

- Chunk size = 128 cubed
- Compressor = blsoc-zstd
- Shuffle = shuffle
- Compression level = ???

## Compressors

### Write speed

The following graph shows write speed for the Zarr-python 2 library, with write time on the x-axis and compression ratio on the y-axis.
Each compressor is represented with a different colour/symbol, and larger markers represent higher compression levels.

![alt text](assets/write_single.png)

The grey cross in the bottom left of the plot shows a baseline result for no compression, taking about 0.7s.
Perhaps surprisingly this has a compression ratio slightly less than one.
This is because the chunk boundaries don't line up exactly with the data shape, so when written to Zarr some extra data at the edges is written to pad the final chunks.

The quickest compressors take around 1 to 2 seconds, and already give comression ratios of ~1.5.
Increasing the compression ratio typically increases the compression ratio at the cost of increased write time.
The compression level does not increase by much - for blosc-zstd going from ~1.8 and write times of 2 seconds to ~2.0 and write times of 50 seconds.

![alt text](assets/write_all.png)

### Read

The following graph shows read speed for the Zarr-python 2 library, with read time on the x-axis and compression ratio on the y-axis.
Again, each compressor is represented with a different colour/symbol, and larger markers represent higher compression levels.

![alt text](assets/read_single.png)

The grey cross in the bottom left of the plot shows a baseline result for no compression, taking about 0.6 seconds.

For zstd (pink triangles) read time increases with compression level.
For all other compressors there is no variation of read time with compression level.
For many compressors this is a feature of their design, with a large one-off cost of compressing the data but no slow down in reading the data.
All the compressors have similar read times of around 1 second, apart from zstd and gzip.

![alt text](assets/read.png)

### Shuffle

In addition to setting the compression level, the blosc compressors also allow setting the "shuffle".
This ... _link out to description of shuffle_.

![alt text](assets/shuffle_compression.png)
![alt text](assets/shuffle_read.png)
![alt text](assets/shuffle_write.png)

Using shuffle increases the compression ratio from ~1.5 to ~1.9, and does not substatially change the read or write times.

### Chunk size

## Software libraries
