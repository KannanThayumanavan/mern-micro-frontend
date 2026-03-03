import json
import os
import re
import hashlib
from pathlib import Path
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_AXIOS_VERSION = "1.8.2"
INTEGRITY_PREFIX = "sha512-"

# Workspaces / sub-packages that are expected to contain a package-lock.json.
# Adjust this list to match the actual monorepo layout.
EXPECTED_LOCKFILE_LOCATIONS = [
    REPO_ROOT,
    REPO_ROOT / "client",
    REPO_ROOT / "server",
    REPO_ROOT / "shared",
]


def find_all_lockfiles(root: Path) -> list[Path]:
    """Recursively find every package-lock.json under *root*, skipping node_modules."""
    lockfiles: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune node_modules to avoid scanning installed copies.
        dirnames[:] = [d for d in dirnames if d != "node_modules"]
        if "package-lock.json" in filenames:
            lockfiles.append(Path(dirpath) / "package-lock.json")
    return lockfiles


def load_lockfile(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def extract_axios_entries_v2_v3(data: dict) -> list[dict]:
    """
    Extract every axios package entry from a lockfile.

    npm lockfile v2/v3 stores resolved packages under the top-level
    "packages" key.  The key is a path such as:
        "node_modules/axios"
        "node_modules/some-lib/node_modules/axios"

    npm lockfile v1 stores them under "dependencies" (possibly nested).
    This function handles both formats and returns a flat list of the
    raw package descriptor dicts that correspond to axios.
    """
    entries: list[dict] = []

    # --- lockfileVersion 2 / 3 ---
    packages = data.get("packages", {})
    for pkg_path, pkg_info in packages.items():
        # Match any path segment that is exactly "axios" (not e.g. "axios-mock-adapter")
        if re.search(r"(?:^|/)node_modules/axios$", pkg_path):
            entries.append({"_lockfile_key": pkg_path, **pkg_info})

    # --- lockfileVersion 1 (legacy) ---
    def _walk_deps_v1(deps: dict, parent_key: str = "dependencies") -> None:
        for name, info in deps.items():
            if name == "axios":
                entries.append({"_lockfile_key": f"{parent_key}/axios", **info})
            nested = info.get("dependencies", {})
            if nested:
                _walk_deps_v1(nested, parent_key=f"{parent_key}/{name}/dependencies")

    if "dependencies" in data and not packages:
        _walk_deps_v1(data["dependencies"])

    return entries


def collect_all_axios_entries() -> list[tuple[Path, dict]]:
    """
    Walk the entire monorepo and return (lockfile_path, entry) pairs for
    every axios resolution found.
    """
    results: list[tuple[Path, dict]] = []
    for lockfile in find_all_lockfiles(REPO_ROOT):
        data = load_lockfile(lockfile)
        for entry in extract_axios_entries_v2_v3(data):
            results.append((lockfile, entry))
    return results


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def all_lockfiles() -> list[Path]:
    lockfiles = find_all_lockfiles(REPO_ROOT)
    return lockfiles


@pytest.fixture(scope="session")
def all_axios_entries() -> list[tuple[Path, dict]]:
    return collect_all_axios_entries()


# ---------------------------------------------------------------------------
# Tests — lockfile presence
# ---------------------------------------------------------------------------

class TestLockfilePresence:
    """Verify that the expected lockfiles actually exist in the monorepo."""

    def test_at_least_one_lockfile_exists(self, all_lockfiles):
        assert len(all_lockfiles) >= 1, (
            "No package-lock.json files were found under the repository root "
            f"({REPO_ROOT}).  Ensure the monorepo has been bootstrapped with "
            "`npm install` before running this test suite."
        )

    @pytest.mark.parametrize("workspace", EXPECTED_LOCKFILE_LOCATIONS)
    def test_expected_workspace_lockfile_exists(self, workspace: Path):
        lockfile = workspace / "package-lock.json"
        assert lockfile.exists(), (
            f"Expected package-lock.json not found at {lockfile}.  "
            "Run `npm install` inside that workspace."
        )

    def test_lockfiles_are_valid_json(self, all_lockfiles):
        for lockfile in all_lockfiles:
            try:
                data = load_lockfile(lockfile)
                assert isinstance(data, dict), f"{lockfile} did not parse to a dict."
            except json.JSONDecodeError as exc:
                pytest.fail(f"{lockfile} contains invalid JSON: {exc}")

    def test_lockfiles_have_lockfile_version_field(self, all_lockfiles):
        for lockfile in all_lockfiles:
            data = load_lockfile(lockfile)
            assert "lockfileVersion" in data, (
                f"{lockfile} is missing the 'lockfileVersion' field — "
                "it may be corrupted or generated by an unsupported npm version."
            )


# ---------------------------------------------------------------------------
# Tests — axios is present in the dependency tree
# ---------------------------------------------------------------------------

class TestAxiosPresence:
    """Verify that axios appears in at least one lockfile (sanity check)."""

    def test_axios_is_resolved_in_monorepo(self, all_axios_entries):
        assert len(all_axios_entries) >= 1, (
            "axios was not found in any package-lock.json across the monorepo.  "
            "Either axios is not a dependency or the lockfiles have not been generated."
        )

    def test_axios_present_in_each_expected_workspace(self):
        """Each expected workspace lockfile should resolve axios."""
        for workspace in EXPECTED_LOCKFILE_LOCATIONS:
            lockfile = workspace / "package-lock.json"
            if not lockfile.exists():
                pytest.skip(f"Lockfile not found at {lockfile}; skipping workspace check.")
            data = load_lockfile(lockfile)
            entries = extract_axios_entries_v2_v3(data)
            assert len(entries) >= 1, (
                f"axios was not found in {lockfile}.  "
                "Ensure axios is listed as a dependency in that workspace."
            )


# ---------------------------------------------------------------------------
# Tests — axios version pinned to exactly 1.8.2
# ---------------------------------------------------------------------------

class TestAxiosVersionPinning:
    """Every resolved axios entry must be exactly version 1.8.2."""

    def test_all_axios_entries_are_version_1_8_2(self, all_axios_entries):
        violations: list[str] = []
        for lockfile, entry in all_axios_entries:
            version = entry.get("version", "<missing>")
            if version != REQUIRED_AXIOS_VERSION:
                violations.append(
                    f"  {lockfile} [{entry.get('_lockfile_key', '?')}] "
                    f"→ version={version!r} (expected {REQUIRED_AXIOS_VERSION!r})"
                )
        assert not violations, (
            f"Found {len(violations)} axios resolution(s) that are NOT pinned to "
            f"{REQUIRED_AXIOS_VERSION}:\n" + "\n".join(violations)
        )

    @pytest.mark.parametr