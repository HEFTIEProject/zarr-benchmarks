CHUNK_SIZE = (300, 200, 100)

BLOSC_CLEVEL = (1, 3, 5)  # range 1-9

# possible options are 'bitshuffle', 'shuffle' and 'noshuffle'
BLOSC_SHUFFLE = ("noshuffle",)

# possible options are 'blosclz', 'lz4', 'lz4hc', 'zlib' and 'zstd'
BLOSC_CNAME = ("zstd",)

GZIP_LEVEL = (1, 3, 5)  # range 1-9

# range 1-22 (according to zstd docs, levels>=20 should be used with caution, as they need more memory)
ZSTD_LEVEL = (1, 7, 13)
