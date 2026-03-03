import json
import os
import pytest


ROOT_PACKAGE_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "package.json",
)

REQUIRED_AXIOS_VERSION = "1.8.2"


def load_root_package_json():
    """Load and parse the root package.json file."""
    if not os.path.exists(ROOT_PACKAGE_JSON_PATH):
        pytest.fail(
            f"Root package.json not found at expected path: {ROOT_PACKAGE_JSON_PATH}"
        )
    with open(ROOT_PACKAGE_JSON_PATH, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            pytest.fail(f"Root package.json is not valid JSON: {exc}")


class TestAxiosOverridesBlockExists:
    """Verify the 'overrides' block is present in root package.json."""

    def test_overrides_key_present_in_package_json(self):
        """Happy path: root package.json must contain an 'overrides' top-level key."""
        data = load_root_package_json()
        assert "overrides" in data, (
            "Root package.json is missing the 'overrides' block. "
            "An 'overrides' block is required to force transitive dependency resolution."
        )

    def test_overrides_value_is_a_dict(self):
        """Happy path: the 'overrides' value must be a JSON object (dict)."""
        data = load_root_package_json()
        assert "overrides" in data, (
            "Root package.json is missing the 'overrides' block."
        )
        assert isinstance(data["overrides"], dict), (
            f"Expected 'overrides' to be a dict, got {type(data['overrides']).__name__}."
        )

    def test_overrides_is_not_empty(self):
        """Happy path: the 'overrides' block must not be an empty object."""
        data = load_root_package_json()
        assert "overrides" in data, (
            "Root package.json is missing the 'overrides' block."
        )
        assert len(data["overrides"]) > 0, (
            "The 'overrides' block in root package.json is empty. "
            "It must contain at least the axios override."
        )


class TestAxiosOverrideVersion:
    """Verify that overrides.axios is set to exactly the required safe version."""

    def test_axios_key_present_in_overrides(self):
        """Happy path: 'axios' must be a key inside the 'overrides' block."""
        data = load_root_package_json()
        assert "overrides" in data, (
            "Root package.json is missing the 'overrides' block."
        )
        overrides = data["overrides"]
        assert "axios" in overrides, (
            f"'axios' is not present in the 'overrides' block. "
            f"Current overrides keys: {list(overrides.keys())}. "
            "Add 'axios': '1.8.2' to force safe transitive resolution."
        )

    def test_axios_override_value_is_string(self):
        """Happy path: the axios override value must be a string."""
        data = load_root_package_json()
        assert "overrides" in data, (
            "Root package.json is missing the 'overrides' block."
        )
        overrides = data["overrides"]
        assert "axios" in overrides, (
            "'axios' is not present in the 'overrides' block."
        )
        assert isinstance(overrides["axios"], str), (
            f"Expected overrides.axios to be a string, "
            f"got {type(overrides['axios']).__name__}: {overrides['axios']!r}."
        )

    def test_axios_override_equals_required_version(self):
        """Happy path: overrides.axios must equal exactly '1.8.2'."""
        data = load_root_package_json()
        assert "overrides" in data, (
            "Root package.json is missing the 'overrides' block."
        )
        overrides = data["overrides"]
        assert "axios" in overrides, (
            "'axios' is not present in the 'overrides' block."
        )
        actual_version = overrides["axios"]
        assert actual_version == REQUIRED_AXIOS_VERSION, (
            f"overrides.axios is '{actual_version}' but must be exactly "
            f"'{REQUIRED_AXIOS_VERSION}' to close the known CVE surface. "
            "Update the overrides block in root package.json."
        )

    def test_axios_override_not_a_range_or_wildcard(self):
        """Happy path: the axios override must be a pinned version, not a range."""
        data = load_root_package_json()
        assert "overrides" in data, (
            "Root package.json is missing the 'overrides' block."
        )
        overrides = data["overrides"]
        assert "axios" in overrides, (
            "'axios' is not present in the 'overrides' block."
        )
        actual_version = overrides["axios"]
        assert isinstance(actual_version, str), (
            f"overrides.axios must be a string, got {type(actual_version).__name__}."
        )
        forbidden_prefixes = ("^", "~", ">", "<", "*", "x", "X")
        for prefix in forbidden_prefixes:
            assert not actual_version.startswith(prefix), (
                f"overrides.axios is '{actual_version}', which uses a version range "
                f"(starts with '{prefix}'). It must be pinned to exactly "
                f"'{REQUIRED_AXIOS_VERSION}' with no range specifier."
            )
        assert actual_version != "*", (
            "overrides.axios must not be a wildcard '*'. "
            f"Pin it to exactly '{REQUIRED_AXIOS_VERSION}'."
        )

    def test_axios_override_version_format_is_semver(self):
        """Happy path: the axios override value must follow MAJOR.MINOR.PATCH semver."""
        data = load_root_package_json()
        assert "overrides" in data, (
            "Root package.json is missing the 'overrides' block."
        )
        overrides = data["overrides"]
        assert "axios" in overrides, (
            "'axios' is not present in the 'overrides' block."
        )
        actual_version = overrides["axios"]
        assert isinstance(actual_version, str), (
            f"overrides.axios must be a string, got {type(actual_version).__name__}."
        )
        parts = actual_version.split(".")
        assert len(parts) == 3, (
            f"overrides.axios '{actual_version}' does not look like a valid "
            "MAJOR.MINOR.PATCH semver string."
        )
        for part in parts:
            assert part.isdigit(), (
                f"overrides.axios '{actual_version}' contains non-numeric segment "
                f"'{part}'. It must be a plain semver like '1.8.2'."
            )


class TestAxiosOverrideErrorPaths:
    """Error-path tests: simulate missing or incorrect overrides configurations."""

    def test_missing_overrides_block_detection(self):
        """Error path: detect when 'overrides' block is absent from package.json data."""
        fake_data = {
            "name": "my-monorepo",
            "version": "1.0.0",
            "dependencies": {"axios": "1.7.0"},
        }
        assert "overrides" not in fake_data, (
            "Test setup error: fake_data should not have 'overrides'."
        )
        with pytest