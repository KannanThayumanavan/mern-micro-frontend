import subprocess
import json
import os
import pytest
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]

PACKAGE_DIRS = {
    "root": REPO_ROOT,
    "client": REPO_ROOT / "client",
    "server": REPO_ROOT / "server",
}

HIGH_SEVERITY_LEVELS = {"high", "critical"}


def _run_npm_audit(directory: Path) -> dict:
    """
    Run `npm audit --json` in *directory* and return the parsed JSON output.

    npm audit exits with a non-zero code when vulnerabilities are found, so we
    must NOT use check=True.  We capture stdout regardless of the exit code and
    parse it as JSON.
    """
    result = subprocess.run(
        ["npm", "audit", "--json"],
        cwd=str(directory),
        capture_output=True,
        text=True,
        timeout=120,
    )
    raw = result.stdout.strip()
    if not raw:
        # Some npm versions write the JSON to stderr on certain errors
        raw = result.stderr.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"npm audit in '{directory}' produced non-JSON output.\n"
            f"stdout: {result.stdout[:2000]}\n"
            f"stderr: {result.stderr[:2000]}\n"
            f"JSONDecodeError: {exc}"
        )


def _extract_vulnerability_counts(audit_json: dict) -> dict[str, int]:
    """
    Return a mapping of severity -> count extracted from the npm audit JSON.

    npm v6 uses ``vulnerabilities`` at the top level with integer counts.
    npm v7+ uses ``metadata.vulnerabilities``.
    Both shapes are handled here.
    """
    # npm v7+ shape
    metadata = audit_json.get("metadata", {})
    if "vulnerabilities" in metadata:
        return {k.lower(): v for k, v in metadata["vulnerabilities"].items()}

    # npm v6 shape – top-level ``vulnerabilities`` is a dict of severity counts
    top_level = audit_json.get("vulnerabilities", {})
    if top_level and all(isinstance(v, int) for v in top_level.values()):
        return {k.lower(): v for k, v in top_level.items()}

    # npm v6 alternative: metadata at top level
    if "metadata" not in audit_json and "advisories" in audit_json:
        counts: dict[str, int] = {}
        for advisory in audit_json["advisories"].values():
            sev = advisory.get("severity", "unknown").lower()
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    return {}


def _collect_high_critical_details(audit_json: dict) -> list[dict]:
    """
    Return a list of dicts describing every HIGH or CRITICAL vulnerability
    found in the audit report, for use in assertion failure messages.
    """
    findings: list[dict] = []

    # npm v7+ shape: top-level ``vulnerabilities`` is a dict of package objects
    vulnerabilities = audit_json.get("vulnerabilities", {})
    if vulnerabilities and not all(isinstance(v, int) for v in vulnerabilities.values()):
        for pkg_name, pkg_data in vulnerabilities.items():
            severity = pkg_data.get("severity", "unknown").lower()
            if severity in HIGH_SEVERITY_LEVELS:
                via = pkg_data.get("via", [])
                advisory_urls = []
                for item in via:
                    if isinstance(item, dict):
                        url = item.get("url") or item.get("source")
                        if url:
                            advisory_urls.append(str(url))
                findings.append(
                    {
                        "package": pkg_name,
                        "severity": severity,
                        "range": pkg_data.get("range", "unknown"),
                        "advisories": advisory_urls,
                    }
                )
        return findings

    # npm v6 shape: top-level ``advisories`` dict
    advisories = audit_json.get("advisories", {})
    for advisory_id, advisory in advisories.items():
        severity = advisory.get("severity", "unknown").lower()
        if severity in HIGH_SEVERITY_LEVELS:
            findings.append(
                {
                    "package": advisory.get("module_name", "unknown"),
                    "severity": severity,
                    "range": advisory.get("vulnerable_versions", "unknown"),
                    "advisories": [advisory.get("url", "")],
                    "advisory_id": advisory_id,
                }
            )

    return findings


def _package_json_exists(directory: Path) -> bool:
    return (directory / "package.json").exists()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", params=list(PACKAGE_DIRS.keys()))
def package_context(request):
    """
    Parametrised fixture that yields (label, Path) for each package directory.
    The test is skipped automatically when the directory or its package.json
    does not exist (e.g. a monorepo that only has a client/ sub-package).
    """
    label = request.param
    directory = PACKAGE_DIRS[label]

    if not directory.exists():
        pytest.skip(f"Directory '{directory}' does not exist – skipping '{label}' audit.")

    if not _package_json_exists(directory):
        pytest.skip(
            f"No package.json found in '{directory}' – skipping '{label}' audit."
        )

    return label, directory


@pytest.fixture(scope="session")
def audit_results_cache():
    """
    Session-scoped cache so that each directory is only audited once even if
    multiple test functions reference the same fixture.
    """
    return {}


# ---------------------------------------------------------------------------
# Core gate test
# ---------------------------------------------------------------------------

class TestNpmAuditGate:
    """
    Security-level tests (SLT) that assert npm audit reports zero HIGH or
    CRITICAL vulnerabilities across all package directories.
    """

    def test_no_high_or_critical_vulnerabilities(self, package_context, audit_results_cache):
        """
        Happy path: npm audit must report 0 HIGH and 0 CRITICAL vulnerabilities.

        This is the primary CI/CD gate.  A failure here means that the
        overrides / resolutions declared in package.json have NOT successfully
        eliminated all known vulnerable transitive dependencies.
        """
        label, directory = package_context

        # Use cached result to avoid running npm audit twice for the same dir
        if label not in audit_results_cache:
            audit_results_cache[label] = _run_npm_audit(directory)

        audit_json = audit_results_cache[label]
        counts = _extract_vulnerability_counts(audit_json)

        high_count = counts.get("high", 0)
        critical_count = counts.get("critical", 0)

        details = _collect_high_critical_details(audit_json)
        detail_str = json.dumps(details, indent=2) if details else "(none)"

        assert high_count == 0 and critical_count == 0, (
            f"\n[{label}] npm audit found HIGH/CRITICAL vulnerabilities that must be "
            f"resolved before merging.\n"
            f"  HIGH:     {high_count}\n"
            f"  CRITICAL: {critical_count}\n"
            f"\nAffected packages:\n{detail_str}\n"
            f"\nRemediation: add/update 'overrides' (npm >=8) or 'resolutions' (yarn) "
            f"in {directory / 'package.json'} to pin vulnerable transitive deps to "
            f"safe versions, then re-run `npm install`."
        )

    def test_audit_json_is_well_formed(self, package_context,