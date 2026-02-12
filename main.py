#!/usr/bin/env python3
import sys
import os
import argparse
from agents.agent1_security_analyzer.scan import scan_local, scan_pr

def print_banner():
    print("╔══════════════════════════════════════════════════╗")
    print("║    🛡️  Shift-Left Security Guardian (Python)     ║")
    print("╚══════════════════════════════════════════════════╝\n")

def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Security Agent Scanner")
    parser.add_argument("--local", nargs="+", help="Scan local files or directories")
    args = parser.parse_args()

    if args.local:
        # ── Local mode ──────────────────────────────────────────────────
        print("📂  Mode: LOCAL")
        print(f"📁  Targets: {', '.join(args.local)}\n")

        print("── Agent-1: Security Analyzer ──────────────────────")
        result = scan_local(args.local)
        issues = result.get("issues", [])
        
        print(f"   Found {len(issues)} issue(s).\n")
        
        # Simple report to stdout
        if issues:
            print("## Security Report")
            for i, issue in enumerate(issues, 1):
                print(f"{i}. [{issue['severity']}] {issue['type']} in {issue['file']}:{issue['line']}")
                print(f"   Code: {issue['code_snippet']}")
                print("-" * 40)
        
        sys.exit(1 if issues else 0)

    else:
        # ── PR mode (GitHub Actions) ────────────────────────────────────
        token = os.environ.get("GITHUB_TOKEN")
        repo_full = os.environ.get("GITHUB_REPOSITORY")
        pr_number_str = os.environ.get("PR_NUMBER")

        if not token or not repo_full or not pr_number_str:
            print("❌  Missing env vars. Required: GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER")
            print("    Tip: use --local for local testing.")
            sys.exit(1)

        pr_number = int(pr_number_str)
        owner, repo_name = repo_full.split("/")
        
        print("🔗  Mode: PULL REQUEST")
        print(f"📦  Repo: {owner}/{repo_name}  •  PR #{pr_number}\n")

        print("── Agent-1: Security Analyzer ──────────────────────")
        result = scan_pr(token, owner, repo_name, pr_number)
        issues = result.get("issues", [])
        
        print(f"   Found {len(issues)} issue(s).\n")

        if issues:
            # Write key=value to GITHUB_OUTPUT for downstream steps
            if "GITHUB_OUTPUT" in os.environ:
                with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                    f.write(f"issues_count={len(issues)}\n")
            
            # Print details to console logs
            for i, issue in enumerate(issues, 1):
                print(f"::warning content={issue['type']}::{issue['file']}:{issue['line']} [{issue['severity']}]")

            sys.exit(1)
        else:
            print("✅  No issues found.")
            sys.exit(0)

if __name__ == "__main__":
    main()
