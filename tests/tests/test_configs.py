from pathlib import Path

import jsonschema
import pytest

from zarr_benchmarks import utils

# mark as tensorstore, so tests in this file are only run once and not for every tox environment
pytestmark = [pytest.mark.tensorstore]


def test_schemas_valid():
    """Validate all jsons in the 'benchmarks_configs' dir against the schema"""

    configs_dir = Path(__file__).parent.parent / "benchmarks" / "benchmark_configs"
    schema = utils.read_json_file(configs_dir / "schema" / "benchmark.schema.json")

    for config_file in configs_dir.glob("*.json"):
        json_to_validate = utils.read_json_file(config_file)
        jsonschema.validate(schema=schema, instance=json_to_validate)
