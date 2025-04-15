parameters = {
    "plot_run_1": {
        "CHUNK_SIZE": [64, 128],
        "BLOSC_CLEVEL": list(range(1, 10)),
        "BLOSC_SHUFFLE": ["shuffle"],
        "BLOSC_CNAME": ["zstd", "blosclz", "lz4", "lz4hc", "zlib"],
        "GZIP_LEVEL": list(range(1, 10)),
        "ZSTD_LEVEL": list(range(1, 20)),
    },
    "plot_run_2": {
        "CHUNK_SIZE": list(range(60, 131)),
        "BLOSC_CLEVEL": 5,
        "BLOSC_SHUFFLE": ["shuffle"],
        "BLOSC_CNAME": ["zstd"],
        "GZIP_LEVEL": [],
        "ZSTD_LEVEL": [],
    },
    "plot_run_3": {
        "CHUNK_SIZE": [64, 128],
        "BLOSC_CLEVEL": 5,
        "BLOSC_SHUFFLE": ["shuffle", "noshuffle", "bitshuffle"],
        "BLOSC_CNAME": ["zstd"],
        "GZIP_LEVEL": [],
        "ZSTD_LEVEL": [],
    },
}
