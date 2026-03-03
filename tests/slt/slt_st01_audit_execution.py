import pytest
import subprocess
import json
import os
import shutil
from pathlib import Path

SECURITY_REPORTS_DIR = Path("docs/security/audit-reports")
ROOT_AUDIT_REPORT = SECURITY_REPORTS_DIR / "root-audit.json"
CLIENT_AUDIT_REPORT = SECURITY_REPORTS_DIR / "client-audit.json"
SERVER_AUDIT_REPORT = SECURITY_REPORTS_DIR / "server-audit.json"
SNYK_REPORT = SECURITY_REPORTS_DIR / "snyk-report.json"
OWASP_REPORT = SECURITY_REPORTS_DIR / "owasp-report.json"

WORKSPACES = {
    "root": ".",
    "client": "client",
    "server": "server",
}

REPORT_PATHS = {
    "root": ROOT_AUDIT_REPORT,
    "client": CLIENT_AUDIT_REPORT,
    "server": SERVER_AUDIT_REPORT,
    "snyk": SNYK_REPORT,
    "owasp": OWASP_REPORT,
}


@pytest.fixture(scope="module", autouse=True)
def ensure_reports_directory():
    SECURITY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    yield


@pytest.fixture(scope="module")
def npm_available():
    result = shutil.which("npm")
    if result is None:
        pytest.skip("npm is not available in PATH")
    return result


@pytest.fixture(scope="module")
def snyk_available():
    result = shutil.which("snyk")
    if result is None:
        pytest.skip("snyk is not available in PATH")
    return result


@pytest.fixture(scope="module")
def dependency_check_available():
    result = shutil.which("dependency-check") or shutil.which("dependency-check.sh")
    if result is None:
        pytest.skip("OWASP dependency-check is not available in PATH")
    return result


def run_command(cmd, cwd=None, timeout=300):
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result
    except subprocess.TimeoutExpired as exc:
        pytest.fail(f"Command timed out after {timeout}s: {' '.join(cmd)}")
    except FileNotFoundError as exc:
        pytest.fail(f"Command not found: {' '.join(cmd)} — {exc}")


def assert_json_file_non_empty(path: Path):
    assert path.exists(), f"Expected report file does not exist: {path}"
    assert path.stat().st_size > 0, f"Report file is empty: {path}"
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read().strip()
    assert content, f"Report file has no readable content: {path}"
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        pytest.fail(f"Report file is not valid JSON: {path} — {exc}")
    assert parsed is not None, f"Parsed JSON is None: {path}"
    return parsed


class TestNpmAuditRootWorkspace:
    def test_npm_audit_root_command_executes(self, npm_available):
        cmd = ["npm", "audit", "--json"]
        result = run_command(cmd, cwd=WORKSPACES["root"])
        assert result is not None, "npm audit command returned no result for root workspace"

    def test_npm_audit_root_produces_output(self, npm_available):
        cmd = ["npm", "audit", "--json"]
        result = run_command(cmd, cwd=WORKSPACES["root"])
        combined_output = result.stdout + result.stderr
        assert combined_output.strip(), "npm audit produced no output for root workspace"

    def test_npm_audit_root_output_is_json(self, npm_available):
        cmd = ["npm", "audit", "--json"]
        result = run_command(cmd, cwd=WORKSPACES["root"])
        output = result.stdout.strip()
        assert output, f"npm audit stdout is empty for root workspace. stderr: {result.stderr}"
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError as exc:
            pytest.fail(f"npm audit root output is not valid JSON: {exc}\nOutput: {output[:500]}")
        assert isinstance(parsed, dict), "npm audit root JSON output is not a dict"

    def test_npm_audit_root_report_written_to_file(self, npm_available):
        cmd = ["npm", "audit", "--json"]
        result = run_command(cmd, cwd=WORKSPACES["root"])
        output = result.stdout.strip()
        assert output, f"npm audit stdout is empty for root. stderr: {result.stderr}"
        ROOT_AUDIT_REPORT.write_text(output, encoding="utf-8")
        assert ROOT_AUDIT_REPORT.exists(), f"Failed to write root audit report to {ROOT_AUDIT_REPORT}"

    def test_npm_audit_root_report_file_non_empty(self, npm_available):
        if not ROOT_AUDIT_REPORT.exists():
            cmd = ["npm", "audit", "--json"]
            result = run_command(cmd, cwd=WORKSPACES["root"])
            ROOT_AUDIT_REPORT.write_text(result.stdout.strip(), encoding="utf-8")
        parsed = assert_json_file_non_empty(ROOT_AUDIT_REPORT)
        assert parsed is not None

    def test_npm_audit_root_report_path_matches_expected(self, npm_available):
        expected = SECURITY_REPORTS_DIR / "root-audit.json"
        assert ROOT_AUDIT_REPORT == expected, (
            f"Root audit report path mismatch: got {ROOT_AUDIT_REPORT}, expected {expected}"
        )

    def test_npm_audit_root_return_code_is_not_crash(self, npm_available):
        cmd = ["npm", "audit", "--json"]
        result = run_command(cmd, cwd=WORKSPACES["root"])
        assert result.returncode in (0, 1), (
            f"npm audit root exited with unexpected code {result.returncode}. "
            f"stderr: {result.stderr[:300]}"
        )


class TestNpmAuditClientWorkspace:
    def test_npm_audit_client_command_executes(self, npm_available):
        client_path = WORKSPACES["client"]
        if not Path(client_path).exists():
            pytest.skip(f"Client workspace directory does not exist: {client_path}")
        cmd = ["npm", "audit", "--json"]
        result = run_command(cmd, cwd=client_path)
        assert result is not None

    def test_npm_audit_client_produces_output(self, npm_available):
        client_path = WORKSPACES["client"]
        if not Path(client_path).exists():
            pytest.skip(f"Client workspace directory does not exist: {client_path}")
        cmd = ["npm", "audit", "--json"]
        result = run_command(cmd, cwd=client_path)
        combined_output = result.stdout + result.stderr
        assert combined_output.strip(), "npm audit produced no output for client workspace"

    def test_npm_audit_client_output_is_json(self, npm_available):
        client_path = WORKSPACES["client"]
        if not Path(client_path).exists():
            pytest.skip(f"Client workspace directory does not exist: {client_path}")
        cmd = ["npm", "audit", "--json"]
        result = run_command(cmd, cwd=client_path)
        output = result.stdout.strip()
        assert output, f"npm audit stdout is empty for client. stderr: {result.stderr}"
        try: