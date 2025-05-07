from typing import Literal

import numcodecs


def get_numcodec_shuffle(shuffle: Literal["shuffle", "noshuffle", "bitshuffle"]) -> int:
    match shuffle:
        case "shuffle":
            return numcodecs.Blosc.SHUFFLE
        case "noshuffle":
            return numcodecs.Blosc.NOSHUFFLE
        case "bitshuffle":
            return numcodecs.Blosc.BITSHUFFLE
        case _:
            raise ValueError(f"invalid shuffle value for blosc {shuffle}")
