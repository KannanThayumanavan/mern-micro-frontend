import pytest
import subprocess
import os
import re
from typing import List, Tuple, Optional


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

REQUIRED_BRANCHES = [
    "feature/SCRUM-29",
    "feature/SCRUM-29-phase-1-audit",
    "feature/SCRUM-29-phase-2-dependency-patching",
    "feature/SCRUM-29-phase-3-runtime-hardening",
    "feature/SCRUM-29-phase-4-auth-uplift",
    "feature/SCRUM-29-phase-5-crypto-uplift",
    "feature/SCRUM-29-phase-6-validation",
]

BASE_BRANCH = "main"


def run_git(args: List[str], cwd: str = REPO_ROOT) -> Tuple[int, str, str]:
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_all_branches() -> List[str]:
    returncode, stdout, stderr = run_git(
        ["branch", "--all", "--format=%(refname:short)"]
    )
    if returncode != 0:
        raise RuntimeError(f"Failed to list branches: {stderr}")
    branches = []
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("origin/"):
            line = line[len("origin/"):]
        if line and line not in branches:
            branches.append(line)
    return branches


def branch_exists(branch_name: str) -> bool:
    all_branches = get_all_branches()
    return branch_name in all_branches


def get_merge_base(branch_a: str, branch_b: str) -> Optional[str]:
    returncode, stdout, stderr = run_git(
        ["merge-base", branch_a, branch_b]
    )
    if returncode != 0:
        return None
    return stdout.strip()


def get_branch_tip(branch_name: str) -> Optional[str]:
    returncode, stdout, stderr = run_git(
        ["rev-parse", branch_name]
    )
    if returncode != 0:
        returncode, stdout, stderr = run_git(
            ["rev-parse", f"origin/{branch_name}"]
        )
        if returncode != 0:
            return None
    return stdout.strip()


def is_branched_from(branch_name: str, base_branch: str) -> bool:
    base_tip = get_branch_tip(base_branch)
    if base_tip is None:
        return False
    merge_base = get_merge_base(branch_name, base_branch)
    if merge_base is None:
        return False
    returncode, stdout, stderr = run_git(
        ["log", "--oneline", f"{merge_base}..{base_branch}"]
    )
    if returncode != 0:
        return False
    commits_ahead = stdout.strip()
    if commits_ahead:
        return True
    returncode2, stdout2, stderr2 = run_git(
        ["rev-parse", base_branch]
    )
    if returncode2 != 0:
        return False
    base_current_tip = stdout2.strip()
    return merge_base == base_current_tip or merge_base is not None


def check_mergeable_without_conflicts(branch_name: str, base_branch: str) -> Tuple[bool, str]:
    returncode, stdout, stderr = run_git(
        ["merge-tree", f"$(git merge-base {branch_name} {base_branch})", base_branch, branch_name]
    )

    merge_base_rc, merge_base_out, merge_base_err = run_git(
        ["merge-base", base_branch, branch_name]
    )
    if merge_base_rc != 0:
        return False, f"Could not find merge base: {merge_base_err}"

    merge_base_sha = merge_base_out.strip()

    returncode, stdout, stderr = run_git(
        ["merge-tree", merge_base_sha, base_branch, branch_name]
    )

    if returncode != 0:
        return False, f"merge-tree failed: {stderr}"

    conflict_markers = ["<<<<<<<", ">>>>>>>", "======="]
    for marker in conflict_markers:
        if marker in stdout:
            return False, f"Conflict detected in merge simulation: found '{marker}' in merge-tree output"

    return True, "No conflicts detected"


def resolve_branch_ref(branch_name: str) -> Optional[str]:
    returncode, stdout, stderr = run_git(["rev-parse", "--verify", branch_name])
    if returncode == 0:
        return stdout.strip()
    returncode, stdout, stderr = run_git(["rev-parse", "--verify", f"origin/{branch_name}"])
    if returncode == 0:
        return stdout.strip()
    returncode, stdout, stderr = run_git(["rev-parse", "--verify", f"refs/remotes/origin/{branch_name}"])
    if returncode == 0:
        return stdout.strip()
    return None


def get_commit_log(branch_name: str, base_branch: str) -> List[str]:
    returncode, stdout, stderr = run_git(
        ["log", "--oneline", f"{base_branch}..{branch_name}"]
    )
    if returncode != 0:
        return []
    return [line.strip() for line in stdout.splitlines() if line.strip()]


class TestBranchExistence:

    def test_base_branch_exists(self):
        assert branch_exists(BASE_BRANCH), (
            f"Base branch '{BASE_BRANCH}' does not exist in the repository. "
            f"All feature branches must be derived from '{BASE_BRANCH}'."
        )

    @pytest.mark.parametrize("branch_name", REQUIRED_BRANCHES)
    def test_required_branch_exists(self, branch_name):
        ref = resolve_branch_ref(branch_name)
        assert ref is not None, (
            f"Required branch '{branch_name}' does not exist in the repository. "
            f"Expected branches: {REQUIRED_BRANCHES}"
        )

    def test_all_required_branches_present(self):
        missing = []
        for branch_name in REQUIRED_BRANCHES:
            ref = resolve_branch_ref(branch_name)
            if ref is None:
                missing.append(branch_name)
        assert not missing, (
            f"The following required branches are missing from the repository: {missing}. "
            f"All of {REQUIRED_BRANCHES} must exist."
        )

    def test_no_unexpected_scrum29_branches(self):
        all_branches = get_all_branches()
        scrum29_branches = [b for b in all_branches if "SCRUM-29" in b]
        unexpected = [b for b in scrum29_branches if b not in REQUIRED_BRANCHES]
        assert not unexpected, (
            f"Unexpected SCRUM-29 branches found: {unexpected}. "
            f"Only the following branches are expected: {REQUIRED_BRANCHES}"
        )

    def test_branch_count_matches_expected(self):
        all_branches = get_all_branches()
        scrum29_branches = [b for b in all_branches if "SCRUM-29" in b]
        assert len(scrum29_branches) == len(REQUIRED_BRANCHES), (
            f"Expected {len(REQUIRED_BRANCHES)} SCRUM-29 branches, "
            f"found {len(scrum29_branches)}: {scrum29_branches}"
        )


class TestBranchOrigin:

    @pytest.mark.parametrize