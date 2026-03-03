import os
import re
import pytest

# ---------------------------------------------------------------------------
# Helpers / constants
# ---------------------------------------------------------------------------

# Directories that must contain an .npmrc file with registry scoping config.
# Adjust these paths relative to the repository root if the monorepo layout
# differs.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

REQUIRED_NPMRC_LOCATIONS = [
    REPO_ROOT,
    os.path.join(REPO_ROOT, "client"),
    os.path.join(REPO_ROOT, "server"),
    os.path.join(REPO_ROOT, "shared"),
]

# Regex patterns that MUST appear in every .npmrc file.
# A registry scoping entry looks like:  @scope:registry=https://...
# or a bare:                            registry=https://...
REGISTRY_SCOPE_PATTERN = re.compile(
    r"(@[\w\-]+:registry\s*=\s*https?://|^registry\s*=\s*https?://)",
    re.MULTILINE,
)

# Flags that must NOT be explicitly disabled (set to false).
MUST_NOT_BE_FALSE = [
    "audit",
    "package-lock",
]

# Flags that, when present, must be set to true (or simply present without =false).
PREFERRED_TRUE_FLAGS = [
    "audit",
    "package-lock",
]


def _npmrc_path(directory: str) -> str:
    return os.path.join(directory, ".npmrc")


def _read_npmrc(directory: str) -> str:
    path = _npmrc_path(directory)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _flag_is_explicitly_false(content: str, flag: str) -> bool:
    """Return True if the flag is explicitly set to false in the content."""
    pattern = re.compile(
        r"^\s*" + re.escape(flag) + r"\s*=\s*false\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    return bool(pattern.search(content))


def _flag_is_set_true(content: str, flag: str) -> bool:
    """Return True if the flag is explicitly set to true in the content."""
    pattern = re.compile(
        r"^\s*" + re.escape(flag) + r"\s*=\s*true\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    return bool(pattern.search(content))


# ---------------------------------------------------------------------------
# Parametrised fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=REQUIRED_NPMRC_LOCATIONS, ids=[
    os.path.relpath(d, REPO_ROOT) or "root" for d in REQUIRED_NPMRC_LOCATIONS
])
def npmrc_directory(request):
    return request.param


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

class TestNpmrcFileExists:
    """Verify that .npmrc files are present in all required locations."""

    def test_npmrc_exists_at_location(self, npmrc_directory):
        path = _npmrc_path(npmrc_directory)
        assert os.path.isfile(path), (
            f".npmrc file is missing at expected location: {path}\n"
            "Every workspace directory and the repo root must contain an .npmrc "
            "file with registry scoping configuration."
        )

    def test_npmrc_is_not_empty(self, npmrc_directory):
        content = _read_npmrc(npmrc_directory)
        assert content.strip(), (
            f".npmrc at {npmrc_directory} exists but is empty. "
            "It must contain registry scoping and integrity settings."
        )


class TestRegistryScopingConfiguration:
    """Verify that registry URL scoping entries are present."""

    def test_registry_scope_entry_present(self, npmrc_directory):
        content = _read_npmrc(npmrc_directory)
        assert REGISTRY_SCOPE_PATTERN.search(content), (
            f".npmrc at {npmrc_directory} does not contain a registry scoping entry.\n"
            "Expected at least one line matching:\n"
            "  @scope:registry=https://... OR registry=https://...\n"
            f"Actual content:\n{content}"
        )

    def test_registry_url_uses_https(self, npmrc_directory):
        content = _read_npmrc(npmrc_directory)
        # Find all registry assignments and ensure none use plain http.
        http_only_pattern = re.compile(
            r"(@[\w\-]+:registry\s*=\s*http://|^registry\s*=\s*http://)",
            re.MULTILINE,
        )
        assert not http_only_pattern.search(content), (
            f".npmrc at {npmrc_directory} contains a registry URL using plain HTTP. "
            "All registry URLs must use HTTPS to prevent MITM attacks."
        )

    def test_registry_scope_entry_has_valid_url(self, npmrc_directory):
        content = _read_npmrc(npmrc_directory)
        # Extract all registry values and validate they look like URLs.
        url_pattern = re.compile(
            r"(?:@[\w\-]+:registry|^registry)\s*=\s*(https?://\S+)",
            re.MULTILINE,
        )
        matches = url_pattern.findall(content)
        assert matches, (
            f".npmrc at {npmrc_directory} has no parseable registry URL values."
        )
        for url in matches:
            assert url.startswith("https://"), (
                f"Registry URL '{url}' in .npmrc at {npmrc_directory} "
                "must start with 'https://'."
            )


class TestIntegrityVerificationSettings:
    """Verify that audit and package-lock flags are not disabled."""

    @pytest.mark.parametrize("flag", MUST_NOT_BE_FALSE)
    def test_flag_not_explicitly_disabled(self, npmrc_directory, flag):
        content = _read_npmrc(npmrc_directory)
        assert not _flag_is_explicitly_false(content, flag), (
            f".npmrc at {npmrc_directory} explicitly disables '{flag}' "
            f"(found '{flag}=false'). "
            "This flag must not be disabled as it is required for supply-chain "
            "integrity verification."
        )

    def test_audit_flag_enabled_or_absent(self, npmrc_directory):
        """audit=true is preferred; audit=false is forbidden."""
        content = _read_npmrc(npmrc_directory)
        assert not _flag_is_explicitly_false(content, "audit"), (
            f".npmrc at {npmrc_directory} sets 'audit=false'. "
            "Audit must remain enabled to detect vulnerable dependencies."
        )

    def test_package_lock_flag_enabled_or_absent(self, npmrc_directory):
        """package-lock=true is preferred; package-lock=false is forbidden."""
        content = _read_npmrc(npmrc_directory)
        assert not _flag_is_explicitly_false(content, "package-lock"), (
            f".npmrc at {npmrc_directory} sets 'package-lock=false'. "
            "The lockfile must remain enabled to prevent dependency substitution."
        )

    def test_audit_flag_explicitly_true_when_present(self, npmrc_directory):
        """If audit flag is present at all, it must be true."""
        content = _read_npmrc(npmrc_directory)
        audit_present = re.search(
            r"^\s*audit\s*=", content, re.MULTILINE | re.IGNORECASE
        )
        if audit_present:
            assert _flag_is_set_true(content, "audit"), (
                f".npmrc at {npmrc_directory} contains an 'audit'