import zarr

CHUNK_SIZE = (300, 200, 100)

BLOSC_CLEVEL = (1, 3, 5)  # range 1-9

# possible options are BloscShuffle.bitshuffle, BloscShuffle.shuffle and BloscShuffle.noshuffle
BLOSC_SHUFFLE = (zarr.codecs.BloscShuffle.noshuffle,)

# possible options are BloscCname.blosclz, BloscCname.lz4, BloscCname.lz4hc, BloscCname.zlib and BloscCname.zstd
BLOSC_CNAME = (zarr.codecs.BloscCname.zstd,)

GZIP_LEVEL = (1, 3, 5)  # range 1-9

# range 1-22 (according to zstd docs, levels>=20 should be used with caution, as they need more memory)
ZSTD_LEVEL = (1, 7, 13)
