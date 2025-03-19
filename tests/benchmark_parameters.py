import zarr

CHUNK_SIZE = (300, 200, 100)

BLOSC_CLEVEL = (1, 3, 5)  # range 1-9
BLOSC_SHUFFLE = (
    # zarr.codecs.BloscShuffle.bitshuffle,
    # zarr.codecs.BloscShuffle.shuffle,
    zarr.codecs.BloscShuffle.noshuffle,
)
BLOSC_CNAME = (
    # zarr.codecs.BloscCname.blosclz,
    # zarr.codecs.BloscCname.lz4,
    # zarr.codecs.BloscCname.lz4hc,
    # zarr.codecs.BloscCname.zlib,
    zarr.codecs.BloscCname.zstd,
)

GZIP_LEVEL = (1, 3, 5)  # range 1-9

# range 1-22 (according to zstd docs, levels>=20 should be used with caution, as they need more memory)
ZSTD_LEVEL = (1, 7, 13)
