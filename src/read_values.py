import pyperf


def main():
    """Simple example of reading benchmark values from an output json"""
    
    suite = pyperf.BenchmarkSuite.load("bench.json")
    bench = suite.get_benchmark("write_to_zarr-(200, 200, 200)")

    print(suite.get_benchmark_names())
    print(suite.get_benchmarks())
    print(bench.get_values())
    print(bench.mean())
    print(bench.stdev())


if __name__ == "__main__":
    main()