import pytest
import json
import os
import subprocess
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def find_repo_root() -> Path:
    """Walk up from this file until we find a directory containing package.json
    or .git.  Falls back to the directory three levels above this file."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".git").exists() or (current / "package.json").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    # Fallback: assume tests/slt/ -> repo root is two levels up
    return Path(__file__).resolve().parent.parent.parent


REPO_ROOT = find_repo_root()

# Directories that must contain a package-lock.json
EXPECTED_LOCK_DIRS = [
    REPO_ROOT,
    REPO_ROOT / "client",
    REPO_ROOT / "server",
]

# Safe minimum versions for vulnerable packages (inclusive lower bound).
# The lock file must NOT contain any version that is strictly less than these.
SAFE_VERSIONS = {
    "nth-check": "2.0.1",
    "loader-utils": "2.0.4",
    "axios": "1.6.0",
    "react": "18.0.0",  # placeholder; adjust to the project's pinned safe version
}

# Packages that must appear in the overrides / resolutions block of the
# root package.json (or the relevant workspace package.json).
REQUIRED_OVERRIDE_PACKAGES = set(SAFE_VERSIONS.keys())

# Vulnerable version range patterns that must NOT appear in any lock file.
VULNERABLE_PATTERNS = [
    # nth-check < 2.0.1
    re.compile(r'"nth-check":\s*\{[^}]*"version":\s*"([01]\.\d+\.\d+)"', re.DOTALL),
    # loader-utils < 2.0.4 and < 1.4.1
    re.compile(r'"loader-utils":\s*\{[^}]*"version":\s*"([01]\.\d+\.\d+)"', re.DOTALL),
    # axios < 1.6.0
    re.compile(r'"axios":\s*\{[^}]*"version":\s*"0\.\d+\.\d+"', re.DOTALL),
]


def _parse_version(version_str: str):
    """Return a tuple of ints for simple semver comparison, ignoring pre-release."""
    clean = re.sub(r"[^\d.]", "", version_str.split("-")[0])
    parts = clean.split(".")
    try:
        return tuple(int(p) for p in parts[:3])
    except ValueError:
        return (0, 0, 0)


def _version_lt(v1: str, v2: str) -> bool:
    """Return True if v1 < v2."""
    return _parse_version(v1) < _parse_version(v2)


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _git_tracked(path: Path) -> bool:
    """Return True if the file is tracked by git (committed or staged)."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        # git not available in this environment – skip the git check
        pytest.skip("git executable not found; skipping git-tracking assertion")


def _collect_package_versions(lock_data: dict, package_name: str) -> list:
    """
    Collect all resolved versions of *package_name* from a package-lock.json.
    Supports both lockfileVersion 1 (dependencies) and 2/3 (packages).
    """
    versions = []

    # lockfileVersion 2 / 3 – "packages" key
    packages = lock_data.get("packages", {})
    for pkg_path, pkg_info in packages.items():
        # pkg_path looks like "node_modules/nth-check" or
        # "node_modules/css-select/node_modules/nth-check"
        if pkg_path.endswith(f"/{package_name}") or pkg_path == package_name:
            v = pkg_info.get("version", "")
            if v:
                versions.append(v)

    # lockfileVersion 1 – "dependencies" key (recursive)
    def _walk_deps(deps: dict):
        for dep_name, dep_info in deps.items():
            if dep_name == package_name:
                v = dep_info.get("version", "")
                if v:
                    versions.append(v)
            nested = dep_info.get("dependencies", {})
            if nested:
                _walk_deps(nested)

    dependencies = lock_data.get("dependencies", {})
    if dependencies:
        _walk_deps(dependencies)

    return versions


# ---------------------------------------------------------------------------
# Parametrised fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=EXPECTED_LOCK_DIRS, ids=[str(d.relative_to(REPO_ROOT)) for d in EXPECTED_LOCK_DIRS])
def lock_dir(request):
    return request.param


@pytest.fixture()
def lock_path(lock_dir):
    return lock_dir / "package-lock.json"


@pytest.fixture()
def lock_data(lock_path):
    if not lock_path.exists():
        pytest.skip(f"package-lock.json not found at {lock_path}; skipping data-dependent tests")
    return _load_json(lock_path)


# ---------------------------------------------------------------------------
# Test 1 – package-lock.json files exist
# ---------------------------------------------------------------------------

class TestPackageLockExists:
    def test_lock_file_present(self, lock_path):
        """package-lock.json must exist in each expected directory."""
        assert lock_path.exists(), (
            f"Missing package-lock.json at {lock_path}. "
            "Run `npm install` in that directory and commit the result."
        )

    def test_lock_file_is_regular_file(self, lock_path):
        """package-lock.json must be a regular file, not a symlink or directory."""
        assert lock_path.is_file(), f"{lock_path} exists but is not a regular file."

    def test_lock_file_non_empty(self, lock_path):
        """package-lock.json must not be empty."""
        assert lock_path.stat().st_size > 0, f"{lock_path} is empty."


# ---------------------------------------------------------------------------
# Test 2 – lock files are committed to source control
# ---------------------------------------------------------------------------

class TestPackageLockGitTracked:
    def test_lock_file_committed(self, lock_path):
        """package-lock.json must be tracked by git (committed or staged)."""
        if not lock_path.exists():
            pytest.skip(f"{lock_path} does not exist; skipping git check.")
        assert _git_tracked(lock_path), (
            f"{lock_path} is NOT tracked by git. "
            "Commit the file: `git add {lock_path} && git commit`."
        )


# ---------------------------------------------------------------------------
# Test 3 – lock file is valid JSON with expected structure
# ---------------------------------------------------------------------------

class TestPackageLockStructure:
    def test_valid_json(self, lock_path):
        """package-lock.json must be parseable JSON."""
        if not lock_path.exists():
            pytest.skip(f"{lock_path} does not exist.")
        try:
            _load_json(lock_path)
        except json.JSONDecodeError as exc:
            pytest.fail(f"{lock