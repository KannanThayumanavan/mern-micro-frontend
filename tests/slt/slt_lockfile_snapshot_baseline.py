import pytest
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import shutil
import copy


# ---------------------------------------------------------------------------
# Constants / helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = REPO_ROOT / "docs" / "security" / "lockfile-snapshots"
SNAPSHOT_FILENAME = "pre-patch-lock.json"

WORKSPACES = ["root", "client", "server"]

WORKSPACE_PATHS = {
    "root": REPO_ROOT,
    "client": REPO_ROOT / "client",
    "server": REPO_ROOT / "server",
}

PACKAGE_LOCK_FILENAME = "package-lock.json"


def _snapshot_path(workspace: str) -> Path:
    return SNAPSHOT_DIR / workspace / SNAPSHOT_FILENAME


def _package_lock_path(workspace: str) -> Path:
    return WORKSPACE_PATHS[workspace] / PACKAGE_LOCK_FILENAME


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _is_valid_package_lock(data: dict) -> bool:
    """Return True when *data* looks like a package-lock.json document."""
    required_top_level_keys = {"name", "lockfileVersion"}
    return isinstance(data, dict) and required_top_level_keys.issubset(data.keys())


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def snapshot_dir() -> Path:
    return SNAPSHOT_DIR


@pytest.fixture(scope="session")
def workspace_snapshot_paths() -> dict:
    return {ws: _snapshot_path(ws) for ws in WORKSPACES}


@pytest.fixture(scope="session")
def workspace_package_lock_paths() -> dict:
    return {ws: _package_lock_path(ws) for ws in WORKSPACES}


@pytest.fixture()
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    """Isolated snapshot directory for mutation tests."""
    snap = tmp_path / "lockfile-snapshots"
    for ws in WORKSPACES:
        (snap / ws).mkdir(parents=True, exist_ok=True)
    return snap


@pytest.fixture()
def minimal_package_lock() -> dict:
    return {
        "name": "test-package",
        "version": "1.0.0",
        "lockfileVersion": 3,
        "requires": True,
        "packages": {
            "": {
                "name": "test-package",
                "version": "1.0.0",
                "license": "MIT",
            }
        },
    }


@pytest.fixture()
def full_package_lock_v2() -> dict:
    return {
        "name": "my-app",
        "version": "0.0.1",
        "lockfileVersion": 2,
        "requires": True,
        "packages": {
            "": {
                "name": "my-app",
                "version": "0.0.1",
                "dependencies": {"express": "^4.18.2"},
            },
            "node_modules/express": {
                "version": "4.18.2",
                "resolved": "https://registry.npmjs.org/express/-/express-4.18.2.tgz",
                "integrity": "sha512-abc123==",
                "license": "MIT",
            },
        },
        "dependencies": {
            "express": {
                "version": "4.18.2",
                "resolved": "https://registry.npmjs.org/express/-/express-4.18.2.tgz",
                "integrity": "sha512-abc123==",
            }
        },
    }


@pytest.fixture()
def populated_tmp_snapshot_dir(tmp_snapshot_dir: Path, minimal_package_lock: dict) -> Path:
    """Snapshot dir pre-populated with valid snapshots for all workspaces."""
    for ws in WORKSPACES:
        snap_file = tmp_snapshot_dir / ws / SNAPSHOT_FILENAME
        snap_file.write_text(json.dumps(minimal_package_lock, indent=2), encoding="utf-8")
    return tmp_snapshot_dir


# ---------------------------------------------------------------------------
# 1. Snapshot directory existence
# ---------------------------------------------------------------------------


class TestSnapshotDirectoryExists:
    def test_snapshot_base_dir_exists(self, snapshot_dir: Path):
        """The top-level lockfile-snapshots directory must exist."""
        assert snapshot_dir.exists(), (
            f"Snapshot directory not found: {snapshot_dir}. "
            "Run the pre-patch snapshot script before applying dependency changes."
        )

    def test_snapshot_base_dir_is_directory(self, snapshot_dir: Path):
        assert snapshot_dir.is_dir(), f"{snapshot_dir} exists but is not a directory."

    @pytest.mark.parametrize("workspace", WORKSPACES)
    def test_workspace_snapshot_subdir_exists(self, snapshot_dir: Path, workspace: str):
        """Each workspace must have its own sub-directory inside the snapshot dir."""
        ws_dir = snapshot_dir / workspace
        assert ws_dir.exists(), (
            f"Workspace snapshot sub-directory missing: {ws_dir}. "
            f"Snapshot for '{workspace}' workspace was never created."
        )

    @pytest.mark.parametrize("workspace", WORKSPACES)
    def test_workspace_snapshot_subdir_is_directory(self, snapshot_dir: Path, workspace: str):
        ws_dir = snapshot_dir / workspace
        if ws_dir.exists():
            assert ws_dir.is_dir(), f"{ws_dir} exists but is not a directory."


# ---------------------------------------------------------------------------
# 2. Snapshot file existence
# ---------------------------------------------------------------------------


class TestSnapshotFileExists:
    @pytest.mark.parametrize("workspace", WORKSPACES)
    def test_snapshot_file_exists(self, workspace_snapshot_paths: dict, workspace: str):
        """pre-patch-lock.json must exist for every workspace."""
        path = workspace_snapshot_paths[workspace]
        assert path.exists(), (
            f"Snapshot file missing for workspace '{workspace}': {path}. "
            "Ensure the pre-patch snapshot script has been executed."
        )

    @pytest.mark.parametrize("workspace", WORKSPACES)
    def test_snapshot_file_is_regular_file(self, workspace_snapshot_paths: dict, workspace: str):
        path = workspace_snapshot_paths[workspace]
        if path.exists():
            assert path.is_file(), f"{path} exists but is not a regular file."

    @pytest.mark.parametrize("workspace", WORKSPACES)
    def test_snapshot_file_is_not_empty(self, workspace_snapshot_paths: dict, workspace: str):
        path = workspace_snapshot_paths[workspace]
        if path.exists():
            assert path.stat().st_size > 0, (
                f"Snapshot file for workspace '{workspace}' is empty: {path}."
            )

    @pytest.mark.parametrize("workspace", WORKSPACES)
    def test_snapshot_filename_is_correct(self, workspace_snapshot_paths: dict, workspace: str):
        path = workspace_snapshot_paths[workspace]
        assert path.name == SNAPSHOT_FILENAME, (
            f"Unexpected snapshot filename '{path.name}' for workspace '{workspace}'. "
            f"Expected '{SNAPSHOT_FILENAME}'."
        )


# ---------------------------------------------------------------------------
# 3. Snapshot JSON validity
# ---------------------------------------------------------------------------


class TestSnapshotJsonValidity:
    @pytest.mark.parametrize("workspace", WORKSPACES)
    def test_snapshot_is_valid_json(self, workspace_snapshot_paths: dict, workspace: str):
        """Snapshot file must be parseable as JSON."""
        path = workspace_snapshot_paths[workspace