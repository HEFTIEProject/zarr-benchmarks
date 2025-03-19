import zarr

# CHUNK_SIZE = (400, 300, 200, 100)
CHUNK_SIZE = (100,)
COMPRESSORS = (
    zarr.codecs.GzipCodec(),
    zarr.codecs.BloscCodec(),
    zarr.codecs.ZstdCodec(),
)

BLOSC_CLEVEL = (1, 3, 5, 7, 9)  # range 1-9
BLOSC_SHUFFLE = (
    zarr.codecs.BloscShuffle.bitshuffle,
    zarr.codecs.BloscShuffle.shuffle,
    zarr.codecs.BloscShuffle.noshuffle,
)
BLOSC_CNAME = (
    zarr.codecs.BloscCname.blosclz,
    zarr.codecs.BloscCname.lz4,
    zarr.codecs.BloscCname.lz4hc,
    zarr.codecs.BloscCname.zlib,
    zarr.codecs.BloscCname.zstd,
)
