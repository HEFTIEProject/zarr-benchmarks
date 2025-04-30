from pathlib import Path

import jsonschema

from zarr_benchmarks import utils


def test_schemas_valid():
    """Validate all jsons in the 'benchmarks_configs' dir against the schema"""

    configs_dir = Path("tests/benchmarks/benchmark_configs")
    schema = utils.read_json_file(configs_dir / "schema" / "benchmark.schema.json")

    for config_file in configs_dir.iterdir():
        if not config_file.is_file():
            continue

        json_to_validate = utils.read_json_file(config_file)
        jsonschema.validate(schema=schema, instance=json_to_validate)
