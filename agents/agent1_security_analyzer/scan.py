import os
import re
from typing import List, Dict, Any
from .patterns import PATTERNS

def scan_content(file_path: str, content: str) -> List[Dict[str, Any]]:
    """
    Scan a single file's content for vulnerabilities.
    """
    issues = []
    lines = content.split('\n')

    for idx, line in enumerate(lines):
        line_trimmed = line.strip()
        # Skip empty lines and comments
        if not line_trimmed or line_trimmed.startswith('//') or line_trimmed.startswith('#') or line_trimmed.startswith('*'):
            continue

        for pattern in PATTERNS:
            if pattern.regex.search(line):
                issues.append({
                    "type": pattern.type,
                    "file": file_path,
                    "line": idx + 1,
                    "severity": pattern.severity,
                    "code_snippet": line_trimmed
                })

    return issues

def collect_files(directory: str) -> List[str]:
    """
    Recursively collect all relevant source files under a directory.
    """
    file_list = []
    extensions = {'.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.rb', '.go', '.php'}
    
    for root, dirs, files in os.walk(directory):
        # Skip node_modules and hidden dirs
        dirs[:] = [d for d in dirs if d != 'node_modules' and not d.startswith('.')]
        
        for file in files:
            if os.path.splitext(file)[1] in extensions:
                file_list.append(os.path.join(root, file))
                
    return file_list

def scan_local(targets: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scan local files / directories.
    """
    all_issues = []

    for target in targets:
        if os.path.isdir(target):
            files = collect_files(target)
        else:
            files = [target]

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = os.path.relpath(file_path, os.getcwd())
                issues = scan_content(rel_path, content)
                all_issues.extend(issues)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return {"issues": all_issues}

def scan_pr(token: str, owner: str, repo: str, pr_number: int) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scan files changed in a GitHub Pull Request.
    """
    # Import here to avoid circular dependency or import errors if not installed
    from .github_client import get_pr_files, get_file_content, create_client
    
    client = create_client(token)
    files = get_pr_files(client, owner, repo, pr_number)
    
    all_issues = []
    extensions = {'.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.rb', '.go', '.php'}

    for file_info in files:
        # Only scan added/modified files
        if file_info['status'] == 'removed' or not file_info['patch']:
            continue
            
        # Extension check
        _, ext = os.path.splitext(file_info['filename'])
        if ext not in extensions:
            continue

        try:
            content = get_file_content(client, owner, repo, file_info['filename'], "HEAD")
            issues = scan_content(file_info['filename'], content)
            all_issues.extend(issues)
        except Exception as e:
            print(f"⚠ Could not fetch {file_info['filename']}: {e}")

    return {"issues": all_issues}
