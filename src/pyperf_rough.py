import pyperf
import zarr


def main():
    runner = pyperf.Runner()
    runner.timeit(
        name="sort a sorted list",
        stmt="sorted(s, key=f)",
        setup="f = lambda x: x; s = list(range(1000))"
        )
    runner.timeit(
        name="SORT",
        stmt="sorted(s, key=f)",
        setup="f = lambda x: x; s = list(range(1000))"
        )


if __name__ == "__main__":
    main()