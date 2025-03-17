import pyperf
import zarr

# This gives ModuleNotFoundError: No module named 'packaging' on python 3.12, but seems to work with 3.11 and 3.13
# conda create -n pyperf-env python=3.12
# conda activate pyperf-env
# pip install zarr
# pip install pyperf


def main():
    runner = pyperf.Runner()
    runner.timeit(
        name="sort a sorted list",
        stmt="sorted(s, key=f)",
        setup="f = lambda x: x; s = list(range(1000))",
    )


if __name__ == "__main__":
    main()
