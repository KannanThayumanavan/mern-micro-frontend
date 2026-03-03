import pytest
import json
import os
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_repo_root() -> Path:
    """Walk up from this file until we find a directory containing package.json."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "package.json").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not locate repository root with package.json")


def load_package_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def collect_package_json_paths() -> dict[str, Path]:
    """Return a mapping of label -> Path for every package.json we care about."""
    root = find_repo_root()
    candidates = {
        "root": root / "package.json",
        "client": root / "client" / "package.json",
        "server": root / "server" / "package.json",
    }
    return {label: path for label, path in candidates.items() if path.exists()}


PACKAGE_JSON_PATHS = collect_package_json_paths()

# Safe versions that must appear in overrides / resolutions
REQUIRED_SAFE_VERSIONS = {
    "nth-check": "2.1.1",
    "loader-utils": "2.0.4",
    "axios": "1.6.8",
    "react": "18.2.0",
}

# Regex that matches a leading ^ or ~
UNPINNED_RE = re.compile(r"^[\^~]")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=list(PACKAGE_JSON_PATHS.keys()))
def package_label(request):
    return request.param


@pytest.fixture
def package_data(package_label):
    path = PACKAGE_JSON_PATHS[package_label]
    return load_package_json(path)


@pytest.fixture
def package_path(package_label):
    return PACKAGE_JSON_PATHS[package_label]


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def get_all_direct_dependencies(data: dict) -> dict[str, str]:
    """Merge dependencies, devDependencies, and peerDependencies."""
    combined: dict[str, str] = {}
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        combined.update(data.get(section, {}))
    return combined


def get_overrides_or_resolutions(data: dict) -> dict[str, str]:
    """
    npm uses 'overrides', yarn uses 'resolutions'.
    Return whichever (or both merged) are present.
    """
    result: dict[str, str] = {}
    result.update(data.get("overrides", {}))
    result.update(data.get("resolutions", {}))
    return result


def flatten_overrides(overrides: dict, prefix: str = "") -> dict[str, str]:
    """
    npm overrides can be nested objects.  Flatten them so that the leaf
    package name maps to its pinned version string.

    Example nested structure:
        { "some-package": { "nth-check": "2.1.1" } }
    becomes:
        { "nth-check": "2.1.1" }
    """
    flat: dict[str, str] = {}
    for key, value in overrides.items():
        if isinstance(value, str):
            flat[key] = value
        elif isinstance(value, dict):
            flat.update(flatten_overrides(value, prefix=key))
    return flat


# ---------------------------------------------------------------------------
# Tests: pinned direct dependencies
# ---------------------------------------------------------------------------

class TestPinnedDirectDependencies:
    """All direct dependency version strings must NOT start with ^ or ~."""

    def test_no_caret_in_dependencies(self, package_label, package_data):
        direct_deps = get_all_direct_dependencies(package_data)
        violations = {
            pkg: ver
            for pkg, ver in direct_deps.items()
            if UNPINNED_RE.match(str(ver))
        }
        assert violations == {}, (
            f"[{package_label}] Found unpinned (^/~) direct dependencies: {violations}"
        )

    def test_no_tilde_in_dependencies(self, package_label, package_data):
        """Explicit tilde check for clarity."""
        direct_deps = get_all_direct_dependencies(package_data)
        tilde_violations = {
            pkg: ver
            for pkg, ver in direct_deps.items()
            if str(ver).startswith("~")
        }
        assert tilde_violations == {}, (
            f"[{package_label}] Found tilde-prefixed direct dependencies: {tilde_violations}"
        )

    def test_no_caret_only_violations(self, package_label, package_data):
        """Explicit caret check for clarity."""
        direct_deps = get_all_direct_dependencies(package_data)
        caret_violations = {
            pkg: ver
            for pkg, ver in direct_deps.items()
            if str(ver).startswith("^")
        }
        assert caret_violations == {}, (
            f"[{package_label}] Found caret-prefixed direct dependencies: {caret_violations}"
        )

    def test_version_strings_are_non_empty(self, package_label, package_data):
        direct_deps = get_all_direct_dependencies(package_data)
        empty_versions = {pkg for pkg, ver in direct_deps.items() if not str(ver).strip()}
        assert empty_versions == set(), (
            f"[{package_label}] Dependencies with empty version strings: {empty_versions}"
        )

    def test_version_strings_are_strings(self, package_label, package_data):
        direct_deps = get_all_direct_dependencies(package_data)
        non_string = {pkg: ver for pkg, ver in direct_deps.items() if not isinstance(ver, str)}
        assert non_string == {}, (
            f"[{package_label}] Dependencies with non-string version values: {non_string}"
        )


# ---------------------------------------------------------------------------
# Tests: overrides / resolutions block existence
# ---------------------------------------------------------------------------

class TestOverridesResolutionsBlockExists:
    """At least one package.json must contain an overrides or resolutions block."""

    def test_at_least_one_file_has_overrides_or_resolutions(self):
        found = False
        for label, path in PACKAGE_JSON_PATHS.items():
            data = load_package_json(path)
            if data.get("overrides") or data.get("resolutions"):
                found = True
                break
        assert found, (
            "No package.json file contains an 'overrides' or 'resolutions' block. "
            "At least one must exist to pin transitive dependency safe versions."
        )

    def test_root_package_json_has_overrides_or_resolutions(self):
        if "root" not in PACKAGE_JSON_PATHS:
            pytest.skip("Root package.json not found")
        data = load_package_json(PACKAGE_JSON_PATHS["root"])
        has_block = bool(data.get("overrides") or data.get("resolutions"))
        assert has_block, (
            "Root package.json is missing both 'overrides' and 'resolutions' blocks."
        )


# ---------------------------------------------------------------------------
# Tests: correct safe versions in overrides / resolutions
# ---------------------------------------------------------------------------

class TestSafeVersionsInOverrides:
    """
    Each required safe package must appear in the overrides/resolutions of
    at least one package.json, pinned to the exact required safe version.
    """

    @pytest.mark.parametrize("pkg,required_version", list(REQUIRED_SAFE_VERSIONS.items()))
    def test_safe_version_present_somewhere(self, pkg, required_version):