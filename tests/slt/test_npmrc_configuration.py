import os
import configparser
import pytest


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLIENT_DIR = os.path.join(REPO_ROOT, "client")
SERVER_DIR = os.path.join(REPO_ROOT, "server")

NPMRC_FILENAME = ".npmrc"

REQUIRED_SETTINGS = {
    "save-exact": "true",
}

OPTIONAL_REGISTRY_SETTINGS = [
    "registry",
    "audit-level",
    "fund",
    "package-lock",
]


def parse_npmrc(filepath):
    """
    Parse a .npmrc file into a dictionary.
    .npmrc files use key=value format (INI-like but without sections).
    We prepend a dummy section header to use configparser.
    """
    if not os.path.isfile(filepath):
        return None

    config = configparser.RawConfigParser()
    config.optionxform = str  # preserve case

    with open(filepath, "r") as f:
        content = f.read()

    # Prepend a dummy section so configparser can handle it
    content_with_section = "[npmrc]\n" + content

    config.read_string(content_with_section)

    result = {}
    if config.has_section("npmrc"):
        for key, value in config.items("npmrc"):
            result[key] = value

    return result


def get_npmrc_path(directory):
    return os.path.join(directory, NPMRC_FILENAME)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def root_npmrc_path():
    return get_npmrc_path(REPO_ROOT)


@pytest.fixture(scope="module")
def client_npmrc_path():
    return get_npmrc_path(CLIENT_DIR)


@pytest.fixture(scope="module")
def server_npmrc_path():
    return get_npmrc_path(SERVER_DIR)


@pytest.fixture(scope="module")
def root_npmrc_config(root_npmrc_path):
    return parse_npmrc(root_npmrc_path)


@pytest.fixture(scope="module")
def client_npmrc_config(client_npmrc_path):
    return parse_npmrc(client_npmrc_path)


@pytest.fixture(scope="module")
def server_npmrc_config(server_npmrc_path):
    return parse_npmrc(server_npmrc_path)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def assert_npmrc_exists(path):
    assert os.path.isfile(path), (
        f".npmrc file not found at expected location: {path}\n"
        "A .npmrc file is required to enforce exact versioning and security settings."
    )


def assert_save_exact(config, location_label):
    assert config is not None, f"Could not parse .npmrc at {location_label}"
    value = config.get("save-exact", "").strip().lower()
    assert value == "true", (
        f"[{location_label}] Expected 'save-exact=true' in .npmrc but got "
        f"'save-exact={value!r}'. "
        "Exact versioning must be enforced to prevent unintended dependency upgrades."
    )


def assert_no_insecure_registry(config, location_label):
    """
    Ensure the registry, if set, uses HTTPS.
    """
    registry = config.get("registry", "").strip()
    if registry:
        assert registry.startswith("https://"), (
            f"[{location_label}] Registry URL must use HTTPS. "
            f"Found: {registry!r}"
        )


def assert_audit_level_acceptable(config, location_label):
    """
    If audit-level is set, it must be 'high' or 'critical' (not 'none' or 'low').
    """
    audit_level = config.get("audit-level", "").strip().lower()
    if audit_level:
        acceptable = {"high", "critical", "moderate"}
        assert audit_level in acceptable, (
            f"[{location_label}] 'audit-level' is set to {audit_level!r}. "
            f"Acceptable values are: {acceptable}. "
            "Setting audit-level to 'none' or 'low' bypasses security gates."
        )


# ---------------------------------------------------------------------------
# Tests: File Existence
# ---------------------------------------------------------------------------

class TestNpmrcFileExistence:

    def test_root_npmrc_exists(self, root_npmrc_path):
        """Root directory must contain a .npmrc file."""
        assert_npmrc_exists(root_npmrc_path)

    def test_client_npmrc_exists(self, client_npmrc_path):
        """Client directory must contain a .npmrc file."""
        assert_npmrc_exists(client_npmrc_path)

    def test_server_npmrc_exists(self, server_npmrc_path):
        """Server directory must contain a .npmrc file."""
        assert_npmrc_exists(server_npmrc_path)

    def test_root_npmrc_is_not_empty(self, root_npmrc_path):
        """Root .npmrc must not be an empty file."""
        assert_npmrc_exists(root_npmrc_path)
        size = os.path.getsize(root_npmrc_path)
        assert size > 0, f"Root .npmrc file is empty: {root_npmrc_path}"

    def test_client_npmrc_is_not_empty(self, client_npmrc_path):
        """Client .npmrc must not be an empty file."""
        assert_npmrc_exists(client_npmrc_path)
        size = os.path.getsize(client_npmrc_path)
        assert size > 0, f"Client .npmrc file is empty: {client_npmrc_path}"

    def test_server_npmrc_is_not_empty(self, server_npmrc_path):
        """Server .npmrc must not be an empty file."""
        assert_npmrc_exists(server_npmrc_path)
        size = os.path.getsize(server_npmrc_path)
        assert size > 0, f"Server .npmrc file is empty: {server_npmrc_path}"


# ---------------------------------------------------------------------------
# Tests: save-exact=true (Happy Path)
# ---------------------------------------------------------------------------

class TestSaveExactConfiguration:

    def test_root_npmrc_save_exact_true(self, root_npmrc_path, root_npmrc_config):
        """Root .npmrc must have save-exact=true."""
        assert_npmrc_exists(root_npmrc_path)
        assert_save_exact(root_npmrc_config, "root")

    def test_client_npmrc_save_exact_true(self, client_npmrc_path, client_npmrc_config):
        """Client .npmrc must have save-exact=true."""
        assert_npmrc_exists(client_npmrc_path)
        assert_save_exact(client_npmrc_config, "client")

    def test_server_npmrc_save_exact_true(self, server_npmrc_path, server_npmrc_config):
        """Server .npmrc must have save-exact=true."""
        assert_npmrc_exists(server_npmrc_path)
        assert_save_exact(server_npmrc_config, "server")

    def test_root_save_exact_key_present(self, root_npmrc_path, root_npmrc_config):
        """The key 'save-exact' must be explicitly present in root .npmrc."""
        assert_npmrc_exists(root_npmrc_path)
        assert root_npmrc_config is not None
        assert "save-exact" in root_npmrc_config, (
            "Key 'save-exact' is missing from root .npmrc. "
            "It must be explicitly set to 'true'."
        )

    def test_client_save_exact_key_present(self, client_