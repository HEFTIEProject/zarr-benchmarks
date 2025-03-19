import zarr

CHUNK_SIZE = (400, 300, 200, 100)
COMPRESSORS = (
    zarr.codecs.GzipCodec(),
    zarr.codecs.BloscCodec(),
    zarr.codecs.ZstdCodec(),
)
