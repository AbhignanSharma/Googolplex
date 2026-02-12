"""
🛡️ Security Guardian - GitHub Integration Tools
═══════════════════════════════════════════════════

Tools for integrating with GitHub PRs:
  - Read PR diffs and changed files
  - Post review comments on specific lines
  - Add labels (security-critical, security-warning)
  - Request changes or approve PRs
  - Create patch PRs with security fixes
  - Track historical risk scores

Uses the GitHub REST API via the `requests` library.
Environment variables required:
  - GITHUB_TOKEN: Personal access token or GitHub App token
  - GITHUB_REPOSITORY: owner/repo format (auto-set in GitHub Actions)
"""

import os
import json
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

GITHUB_API = "https://api.github.com"
SECURITY_LABELS = {
    "critical": {"name": "security-critical", "color": "d73a4a", "description": "Critical security vulnerability found"},
    "high": {"name": "security-high", "color": "e99695", "description": "High severity security issue"},
    "medium": {"name": "security-warning", "color": "fbca04", "description": "Medium severity security concern"},
    "low": {"name": "security-info", "color": "0e8a16", "description": "Low severity security note"},
    "clean": {"name": "security-approved", "color": "0e8a16", "description": "Security review passed"},
}

# In-memory risk history (persists across PRs within same process)
_risk_history: dict = {}


def _get_headers() -> dict:
    """Get GitHub API headers with authentication."""
    token = os.environ.get("GITHUB_TOKEN", "")
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get_repo() -> str:
    """Get repository in owner/repo format."""
    return os.environ.get("GITHUB_REPOSITORY", "")


# ═══════════════════════════════════════════════════════════════════
# PR READING TOOLS
# ═══════════════════════════════════════════════════════════════════

def get_pr_diff(pr_number: int) -> dict:
    """Fetch the full diff of a GitHub Pull Request for security review.

    Gets the complete code changes including added, modified, and deleted files.
    This is the primary input for PR-based security reviews.

    Args:
        pr_number: The pull request number to review.

    Returns:
        dict: Contains PR metadata, changed files with diffs, and statistics.
    """
    repo = _get_repo()
    if not repo:
        return {"success": False, "error": "GITHUB_REPOSITORY not set. Set it to 'owner/repo'."}

    headers = _get_headers()
    headers["Accept"] = "application/vnd.github.v3.diff"

    try:
        # Get the diff
        diff_resp = requests.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
            headers=headers, timeout=30
        )
        diff_text = diff_resp.text if diff_resp.status_code == 200 else ""

        # Get PR metadata
        headers["Accept"] = "application/vnd.github.v3+json"
        meta_resp = requests.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
            headers=headers, timeout=15
        )
        meta = meta_resp.json() if meta_resp.status_code == 200 else {}

        # Get changed files list with patches
        files_resp = requests.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/files",
            headers=headers, timeout=15
        )
        files = files_resp.json() if files_resp.status_code == 200 else []

        changed_files = []
        for f in files:
            changed_files.append({
                "filename": f.get("filename", ""),
                "status": f.get("status", ""),  # added, modified, removed, renamed
                "additions": f.get("additions", 0),
                "deletions": f.get("deletions", 0),
                "patch": f.get("patch", ""),
            })

        return {
            "success": True,
            "pr_number": pr_number,
            "title": meta.get("title", ""),
            "author": meta.get("user", {}).get("login", ""),
            "base_branch": meta.get("base", {}).get("ref", ""),
            "head_branch": meta.get("head", {}).get("ref", ""),
            "total_files_changed": len(changed_files),
            "total_additions": sum(f["additions"] for f in changed_files),
            "total_deletions": sum(f["deletions"] for f in changed_files),
            "changed_files": changed_files,
            "full_diff": diff_text[:100000],  # Cap at 100KB
        }

    except Exception as e:
        return {"success": False, "error": f"Error fetching PR: {str(e)}"}


def get_pr_file_content(pr_number: int, filepath: str) -> dict:
    """Fetch the full content of a specific file from a PR's head branch.

    Use this to get complete file context when the diff alone isn't enough
    to understand the security implications.

    Args:
        pr_number: The pull request number.
        filepath: Path to the file within the repository.

    Returns:
        dict: Contains the full file content and metadata.
    """
    repo = _get_repo()
    if not repo:
        return {"success": False, "error": "GITHUB_REPOSITORY not set."}

    headers = _get_headers()

    try:
        # Get PR head ref
        pr_resp = requests.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
            headers=headers, timeout=15
        )
        if pr_resp.status_code != 200:
            return {"success": False, "error": f"PR not found: {pr_resp.status_code}"}

        head_ref = pr_resp.json().get("head", {}).get("ref", "")

        # Get file content at that ref
        file_resp = requests.get(
            f"{GITHUB_API}/repos/{repo}/contents/{filepath}?ref={head_ref}",
            headers=headers, timeout=15
        )
        if file_resp.status_code != 200:
            return {"success": False, "error": f"File not found: {filepath}"}

        import base64
        content = base64.b64decode(file_resp.json().get("content", "")).decode('utf-8', errors='replace')

        return {
            "success": True,
            "filepath": filepath,
            "branch": head_ref,
            "content": content,
            "size": len(content),
        }

    except Exception as e:
        return {"success": False, "error": f"Error fetching file: {str(e)}"}


# ═══════════════════════════════════════════════════════════════════
# PR REVIEW ACTIONS
# ═══════════════════════════════════════════════════════════════════

def post_review_comment(
    pr_number: int,
    body: str,
    event: str = "COMMENT",
    comments: Optional[List[Dict[str, Any]]] = None,
) -> dict:
    """Post a security review on a GitHub Pull Request.

    Can post an overall review summary and/or inline comments on specific
    lines of changed files.

    Args:
        pr_number: The pull request number.
        body: The main review body (markdown supported). This is the summary
              comment that appears at the top of the review.
        event: Review action — 'COMMENT' (neutral), 'REQUEST_CHANGES' (block),
               or 'APPROVE'. Use REQUEST_CHANGES for critical/high issues.
        comments: Optional list of inline comments. Each comment should have:
                  - path: file path
                  - line: line number in the diff
                  - body: comment text (markdown)

    Returns:
        dict: Success status and review URL.
    """
    repo = _get_repo()
    if not repo:
        return {"success": False, "error": "GITHUB_REPOSITORY not set."}

    headers = _get_headers()

    try:
        # Get the latest commit SHA for the PR
        pr_resp = requests.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
            headers=headers, timeout=15
        )
        commit_sha = pr_resp.json().get("head", {}).get("sha", "")

        review_data = {
            "body": body,
            "event": event,
            "commit_id": commit_sha,
        }
        if comments:
            review_data["comments"] = comments

        resp = requests.post(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/reviews",
            headers=headers, json=review_data, timeout=15
        )

        if resp.status_code in (200, 201):
            return {
                "success": True,
                "review_id": resp.json().get("id"),
                "review_url": resp.json().get("html_url", ""),
                "event": event,
            }
        else:
            return {"success": False, "error": f"Review failed: {resp.status_code} — {resp.text}"}

    except Exception as e:
        return {"success": False, "error": f"Error posting review: {str(e)}"}


def add_security_label(pr_number: int, severity: str) -> dict:
    """Add a security severity label to a Pull Request.

    Automatically creates the label if it doesn't exist in the repository.
    Uses color-coded labels for visual severity indication.

    Args:
        pr_number: The pull request number.
        severity: One of 'critical', 'high', 'medium', 'low', 'clean'.

    Returns:
        dict: Success status and label details.
    """
    repo = _get_repo()
    if not repo:
        return {"success": False, "error": "GITHUB_REPOSITORY not set."}

    headers = _get_headers()
    label_config = SECURITY_LABELS.get(severity, SECURITY_LABELS["medium"])

    try:
        # Ensure label exists (create if not)
        requests.post(
            f"{GITHUB_API}/repos/{repo}/labels",
            headers=headers,
            json={
                "name": label_config["name"],
                "color": label_config["color"],
                "description": label_config["description"],
            },
            timeout=10,
        )

        # Add label to PR
        resp = requests.post(
            f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/labels",
            headers=headers,
            json={"labels": [label_config["name"]]},
            timeout=10,
        )

        if resp.status_code == 200:
            return {
                "success": True,
                "label": label_config["name"],
                "severity": severity,
                "pr_number": pr_number,
            }
        else:
            return {"success": False, "error": f"Label failed: {resp.status_code}"}

    except Exception as e:
        return {"success": False, "error": f"Error adding label: {str(e)}"}


# ═══════════════════════════════════════════════════════════════════
# PATCH PR CREATION
# ═══════════════════════════════════════════════════════════════════

def create_patch_pr(
    pr_number: int,
    fixes: List[Dict[str, Any]],
    title: Optional[str] = None,
    body: Optional[str] = None,
) -> dict:
    """Create a patch PR with security fixes for a reviewed Pull Request.

    Creates a new branch from the PR's head branch, applies the security
    fixes as commits, and opens a new PR targeting the original PR's branch.

    Args:
        pr_number: The original PR number that was reviewed.
        fixes: List of file fixes to apply. Each fix should have:
               - filepath: path to the file to fix
               - content: the complete corrected file content
               - message: commit message describing the fix
        title: Optional title for the patch PR. Defaults to
               '🛡️ Security Fix for PR #X'.
        body: Optional body for the patch PR. Defaults to a security summary.

    Returns:
        dict: Success status, new PR number, and URL.
    """
    repo = _get_repo()
    if not repo:
        return {"success": False, "error": "GITHUB_REPOSITORY not set."}

    headers = _get_headers()

    try:
        # Get original PR info
        pr_resp = requests.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
            headers=headers, timeout=15
        )
        pr_data = pr_resp.json()
        head_branch = pr_data.get("head", {}).get("ref", "")
        head_sha = pr_data.get("head", {}).get("sha", "")

        # Create a new branch for the patch
        patch_branch = f"security-fix/pr-{pr_number}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create branch ref
        ref_resp = requests.post(
            f"{GITHUB_API}/repos/{repo}/git/refs",
            headers=headers,
            json={
                "ref": f"refs/heads/{patch_branch}",
                "sha": head_sha,
            },
            timeout=15,
        )

        if ref_resp.status_code not in (200, 201):
            return {"success": False, "error": f"Branch creation failed: {ref_resp.text}"}

        # Apply each fix as a commit
        for fix in fixes:
            filepath = fix.get("filepath", "")
            content = fix.get("content", "")
            message = fix.get("message", f"🛡️ security: fix vulnerability in {filepath}")

            # Get current file SHA (needed for updates)
            file_resp = requests.get(
                f"{GITHUB_API}/repos/{repo}/contents/{filepath}?ref={patch_branch}",
                headers=headers, timeout=15,
            )

            import base64
            update_data = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": patch_branch,
            }

            if file_resp.status_code == 200:
                update_data["sha"] = file_resp.json().get("sha", "")

            commit_resp = requests.put(
                f"{GITHUB_API}/repos/{repo}/contents/{filepath}",
                headers=headers, json=update_data, timeout=15,
            )

            if commit_resp.status_code not in (200, 201):
                return {"success": False, "error": f"Commit failed for {filepath}: {commit_resp.text}"}

        # Create the patch PR
        patch_title = title or f"🛡️ Security Fix for PR #{pr_number}"
        patch_body = body or (
            f"## 🛡️ Security Patch\n\n"
            f"This PR contains automated security fixes for PR #{pr_number}.\n\n"
            f"### Changes\n"
            + "\n".join(f"- `{fix['filepath']}`: {fix.get('message', 'Security fix')}" for fix in fixes)
            + f"\n\n---\n*Generated by Security Guardian*"
        )

        pr_create_resp = requests.post(
            f"{GITHUB_API}/repos/{repo}/pulls",
            headers=headers,
            json={
                "title": patch_title,
                "body": patch_body,
                "head": patch_branch,
                "base": head_branch,
            },
            timeout=15,
        )

        if pr_create_resp.status_code in (200, 201):
            new_pr = pr_create_resp.json()
            return {
                "success": True,
                "patch_pr_number": new_pr.get("number"),
                "patch_pr_url": new_pr.get("html_url"),
                "patch_branch": patch_branch,
                "fixes_applied": len(fixes),
            }
        else:
            return {"success": False, "error": f"PR creation failed: {pr_create_resp.text}"}

    except Exception as e:
        return {"success": False, "error": f"Error creating patch PR: {str(e)}"}


# ═══════════════════════════════════════════════════════════════════
# RISK HISTORY TRACKING
# ═══════════════════════════════════════════════════════════════════

def record_risk_score(pr_number: int, score: float, findings_count: int, severity: str) -> dict:
    """Record the security risk score for a PR to track trends over time.

    Maintains a history of security scores across PRs to show improvement
    or regression trends in the repository's security posture.

    Args:
        pr_number: The pull request number.
        score: The security risk score (0-10).
        findings_count: Number of security findings.
        severity: Overall severity level.

    Returns:
        dict: Current score, historical trend, and comparison with recent PRs.
    """
    global _risk_history

    repo = _get_repo() or "local"

    if repo not in _risk_history:
        _risk_history[repo] = []

    entry = {
        "pr_number": pr_number,
        "score": score,
        "findings": findings_count,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
    }
    _risk_history[repo].append(entry)

    # Calculate trend
    history = _risk_history[repo]
    recent = history[-10:]  # Last 10 reviews

    avg_score = sum(e["score"] for e in recent) / len(recent)
    trend = "improving" if len(recent) > 1 and recent[-1]["score"] < recent[-2]["score"] else \
            "declining" if len(recent) > 1 and recent[-1]["score"] > recent[-2]["score"] else \
            "stable"

    return {
        "success": True,
        "current_score": score,
        "average_recent_score": round(avg_score, 2),
        "trend": trend,
        "total_reviews": len(history),
        "recent_history": [
            {"pr": e["pr_number"], "score": e["score"], "severity": e["severity"]}
            for e in recent
        ],
    }
