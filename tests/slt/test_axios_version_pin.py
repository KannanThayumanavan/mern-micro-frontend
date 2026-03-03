import pytest
import json
import os
from pathlib import Path


MONOREPO_ROOT = Path(__file__).resolve().parents[2]

PACKAGE_JSON_LOCATIONS = [
    MONOREPO_ROOT / "package.json",
    MONOREPO_ROOT / "client" / "package.json",
    MONOREPO_ROOT / "server" / "package.json",
    MONOREPO_ROOT / "shared" / "package.json",
]

EXPECTED_AXIOS_VERSION = "1.8.2"
INVALID_PREFIXES = ("^", "~", ">", "<", ">=", "<=", "*")


def load_package_json(path: Path) -> dict:
    if not path.exists():
        pytest.skip(f"package.json not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_axios_version(package_data: dict, block: str) -> str | None:
    return package_data.get(block, {}).get("axios")


def assert_exact_version(version: str, location: str, block: str):
    assert version is not None, (
        f"axios not found in '{block}' of {location}"
    )
    assert not version.startswith(INVALID_PREFIXES), (
        f"axios version '{version}' in '{block}' of {location} "
        f"must not have a range prefix (^, ~, >, <, >=, <=, *). "
        f"Expected exact version '{EXPECTED_AXIOS_VERSION}'."
    )
    assert version == EXPECTED_AXIOS_VERSION, (
        f"axios version '{version}' in '{block}' of {location} "
        f"does not match expected exact version '{EXPECTED_AXIOS_VERSION}'."
    )


@pytest.mark.parametrize("package_json_path", PACKAGE_JSON_LOCATIONS)
class TestAxiosVersionPin:

    def test_axios_pinned_in_dependencies(self, package_json_path: Path):
        package_data = load_package_json(package_json_path)
        version = get_axios_version(package_data, "dependencies")
        if version is None:
            pytest.skip(
                f"axios not present in 'dependencies' of {package_json_path}"
            )
        assert_exact_version(version, str(package_json_path), "dependencies")

    def test_axios_pinned_in_dev_dependencies(self, package_json_path: Path):
        package_data = load_package_json(package_json_path)
        version = get_axios_version(package_data, "devDependencies")
        if version is None:
            pytest.skip(
                f"axios not present in 'devDependencies' of {package_json_path}"
            )
        assert_exact_version(version, str(package_json_path), "devDependencies")

    def test_axios_present_in_at_least_one_block(self, package_json_path: Path):
        package_data = load_package_json(package_json_path)
        deps_version = get_axios_version(package_data, "dependencies")
        dev_deps_version = get_axios_version(package_data, "devDependencies")
        assert deps_version is not None or dev_deps_version is not None, (
            f"axios is not declared in either 'dependencies' or 'devDependencies' "
            f"in {package_json_path}. It must be pinned to '{EXPECTED_AXIOS_VERSION}'."
        )

    def test_no_caret_prefix_in_dependencies(self, package_json_path: Path):
        package_data = load_package_json(package_json_path)
        version = get_axios_version(package_data, "dependencies")
        if version is None:
            pytest.skip(
                f"axios not present in 'dependencies' of {package_json_path}"
            )
        assert not version.startswith("^"), (
            f"axios version '{version}' in 'dependencies' of {package_json_path} "
            f"uses caret (^) prefix which allows minor/patch upgrades. "
            f"Must be exact: '{EXPECTED_AXIOS_VERSION}'."
        )

    def test_no_tilde_prefix_in_dependencies(self, package_json_path: Path):
        package_data = load_package_json(package_json_path)
        version = get_axios_version(package_data, "dependencies")
        if version is None:
            pytest.skip(
                f"axios not present in 'dependencies' of {package_json_path}"
            )
        assert not version.startswith("~"), (
            f"axios version '{version}' in 'dependencies' of {package_json_path} "
            f"uses tilde (~) prefix which allows patch upgrades. "
            f"Must be exact: '{EXPECTED_AXIOS_VERSION}'."
        )

    def test_no_caret_prefix_in_dev_dependencies(self, package_json_path: Path):
        package_data = load_package_json(package_json_path)
        version = get_axios_version(package_data, "devDependencies")
        if version is None:
            pytest.skip(
                f"axios not present in 'devDependencies' of {package_json_path}"
            )
        assert not version.startswith("^"), (
            f"axios version '{version}' in 'devDependencies' of {package_json_path} "
            f"uses caret (^) prefix which allows minor/patch upgrades. "
            f"Must be exact: '{EXPECTED_AXIOS_VERSION}'."
        )

    def test_no_tilde_prefix_in_dev_dependencies(self, package_json_path: Path):
        package_data = load_package_json(package_json_path)
        version = get_axios_version(package_data, "devDependencies")
        if version is None:
            pytest.skip(
                f"axios not present in 'devDependencies' of {package_json_path}"
            )
        assert not version.startswith("~"), (
            f"axios version '{version}' in 'devDependencies' of {package_json_path} "
            f"uses tilde (~) prefix which allows patch upgrades. "
            f"Must be exact: '{EXPECTED_AXIOS_VERSION}'."
        )

    def test_no_wildcard_version_in_dependencies(self, package_json_path: Path):
        package_data = load_package_json(package_json_path)
        version = get_axios_version(package_data, "dependencies")
        if version is None:
            pytest.skip(
                f"axios not present in 'dependencies' of {package_json_path}"
            )
        assert version != "*", (
            f"axios version is set to wildcard '*' in 'dependencies' of "
            f"{package_json_path}. Must be exact: '{EXPECTED_AXIOS_VERSION}'."
        )
        assert "x" not in version.lower(), (
            f"axios version '{version}' in 'dependencies' of {package_json_path} "
            f"appears to use an 'x' wildcard range. "
            f"Must be exact: '{EXPECTED_AXIOS_VERSION}'."
        )

    def test_no_range_version_in_dependencies(self, package_json_path: Path):
        package_data = load_package_json(package_json_path)
        version = get_axios_version(package_data, "dependencies")
        if version is None:
            pytest.skip(
                f"axios not present in 'dependencies' of {package_json_path}"
            )
        assert not version.startswith(">"), (
            f"axios version '{version}' in 'dependencies' of {package_json_path} "
            f"uses a range specifier. Must be exact: '{EXPECTED_AXIOS_VERSION}'."
        )
        assert not version.start