"""
🛡️ Security Guardian - Tools Module (Enterprise Architecture)
══════════════════════════════════════════════════════════════════

Philosophy: Tools provide DATA, the LLM provides INTELLIGENCE.

These tools do NOT try to detect vulnerabilities — that's the LLM's job.
Instead, they give the LLM agent the ability to:
  1. Read files from the filesystem
  2. Explore project structure
  3. Get git diffs for PR review
  4. Search codebases for context and patterns
  5. Understand project dependencies

The LLM (Gemini) already has deep knowledge of OWASP Top 10, CWE, CVE,
SANS Top 25, NIST guidelines, and every major vulnerability class ever
published. We let IT do the security analysis.
"""

import os
import subprocess
import fnmatch
from typing import Optional


def read_file(filepath: str) -> dict:
    """Read the contents of a file from the filesystem for security analysis.

    Use this tool to read source code files, configuration files, dependency
    manifests, Dockerfiles, CI/CD configs, infrastructure-as-code files, or
    any other file that needs security review.

    Args:
        filepath: Absolute or relative path to the file to read.

    Returns:
        dict: Contains the file content, language, size, and metadata.
              Returns an error message if the file cannot be read.
    """
    try:
        filepath = os.path.expanduser(filepath)
        if not os.path.isfile(filepath):
            return {
                "success": False,
                "error": f"File not found: {filepath}",
                "suggestion": "Use list_files to explore the project structure first."
            }

        file_size = os.path.getsize(filepath)
        if file_size > 500_000:  # 500KB limit
            return {
                "success": False,
                "error": f"File too large ({file_size} bytes). Maximum is 500KB.",
                "suggestion": "For large files, use search_in_code to find specific sections."
            }

        with open(filepath, 'r', errors='replace') as f:
            content = f.read()

        # Detect language from extension
        ext = os.path.splitext(filepath)[1].lower()
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.java': 'java', '.go': 'go', '.rs': 'rust', '.rb': 'ruby',
            '.php': 'php', '.cs': 'csharp', '.cpp': 'cpp', '.c': 'c',
            '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala',
            '.jsx': 'javascript-react', '.tsx': 'typescript-react',
            '.vue': 'vue', '.sql': 'sql', '.sh': 'shell', '.bash': 'shell',
            '.yml': 'yaml', '.yaml': 'yaml', '.json': 'json',
            '.xml': 'xml', '.html': 'html', '.css': 'css',
            '.tf': 'terraform', '.hcl': 'hcl',
            '.dockerfile': 'docker', '.toml': 'toml', '.ini': 'ini',
            '.cfg': 'config', '.conf': 'config', '.env': 'env',
            '.gradle': 'gradle', '.properties': 'java-properties',
        }
        language = lang_map.get(ext, 'unknown')

        # Special filename detection
        basename = os.path.basename(filepath).lower()
        if basename == 'dockerfile':
            language = 'docker'
        elif basename in ('makefile', 'gemfile', 'rakefile'):
            language = 'ruby'
        elif basename in ('.env', '.env.local', '.env.production'):
            language = 'env'
        elif basename in ('docker-compose.yml', 'docker-compose.yaml'):
            language = 'docker-compose'

        line_count = content.count('\n') + 1

        return {
            "success": True,
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "language": language,
            "size_bytes": file_size,
            "line_count": line_count,
            "content": content,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading file: {str(e)}"
        }


def list_files(directory: str, pattern: Optional[str] = None, max_depth: int = 3) -> dict:
    """List files in a directory to understand project structure.

    Use this tool to explore a project's layout before diving into specific
    files. This helps you understand what kind of application it is, what
    frameworks are used, and which files are security-relevant.

    Args:
        directory: Path to the directory to explore.
        pattern: Optional glob pattern to filter files (e.g., '*.py', '*.java',
                 '*.yml'). If not specified, lists all files.
        max_depth: Maximum directory depth to explore (default: 3).

    Returns:
        dict: Contains the project structure with file paths and types.
    """
    try:
        directory = os.path.expanduser(directory)
        if not os.path.isdir(directory):
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }

        files = []
        security_relevant = []

        # Security-relevant file patterns
        security_files = {
            'package.json', 'package-lock.json', 'yarn.lock',
            'requirements.txt', 'Pipfile', 'Pipfile.lock', 'poetry.lock', 'setup.py', 'pyproject.toml',
            'pom.xml', 'build.gradle', 'build.gradle.kts',
            'go.mod', 'go.sum', 'Cargo.toml', 'Cargo.lock',
            'Gemfile', 'Gemfile.lock', 'composer.json', 'composer.lock',
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            '.env', '.env.local', '.env.production', '.env.example',
            '.htaccess', 'nginx.conf', 'apache.conf',
            'web.xml', 'applicationContext.xml',
            'settings.py', 'config.py', 'config.js', 'config.ts',
            '.eslintrc', '.eslintrc.js', '.eslintrc.json',
            'jest.config.js', 'tsconfig.json', 'webpack.config.js',
            'Makefile', 'Jenkinsfile', '.gitlab-ci.yml', '.github',
            'terraform.tf', 'main.tf', 'variables.tf',
            'kubernetes.yml', 'k8s.yml', 'helm',
            'sonar-project.properties', '.snyk',
        }

        for root, dirs, filenames in os.walk(directory):
            # Calculate depth
            depth = root.replace(directory, '').count(os.sep)
            if depth >= max_depth:
                dirs.clear()
                continue

            # Skip common non-relevant directories
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '.git', '__pycache__', '.venv', 'venv',
                'env', '.env', 'dist', 'build', '.next', '.nuxt',
                'target', 'bin', 'obj', '.idea', '.vscode',
                'vendor', '.bundle', '.gradle', '.m2',
                'coverage', '.nyc_output', 'htmlcov',
            }]

            for filename in filenames:
                if pattern and not fnmatch.fnmatch(filename, pattern):
                    continue

                rel_path = os.path.relpath(os.path.join(root, filename), directory)
                file_info = {
                    "path": rel_path,
                    "size": os.path.getsize(os.path.join(root, filename))
                }
                files.append(file_info)

                # Flag security-relevant files
                if filename.lower() in security_files or filename.lower().startswith('.env'):
                    security_relevant.append(rel_path)

        # Limit output
        if len(files) > 200:
            files = files[:200]
            truncated = True
        else:
            truncated = False

        return {
            "success": True,
            "directory": directory,
            "total_files": len(files),
            "truncated": truncated,
            "security_relevant_files": security_relevant,
            "files": files,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error listing directory: {str(e)}"
        }


def get_git_diff(repo_path: str, base_branch: str = "main", target_branch: str = "HEAD") -> dict:
    """Get the git diff between two branches for PR/code review.

    Use this tool to see what changed in a pull request or recent commits.
    This is ideal for reviewing code changes rather than entire files.

    Args:
        repo_path: Path to the git repository root.
        base_branch: The base branch to compare against (default: 'main').
                     Can also be a commit hash or 'HEAD~1' for last commit.
        target_branch: The target branch with changes (default: 'HEAD').

    Returns:
        dict: Contains the diff output, changed files, and statistics.
    """
    try:
        repo_path = os.path.expanduser(repo_path)

        # Check if it's a git repo
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=repo_path, capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Not a git repository: {repo_path}"
            }

        # Get diff
        diff_result = subprocess.run(
            ['git', 'diff', base_branch, target_branch],
            cwd=repo_path, capture_output=True, text=True, timeout=30
        )

        # Get changed files summary
        stat_result = subprocess.run(
            ['git', 'diff', '--stat', base_branch, target_branch],
            cwd=repo_path, capture_output=True, text=True, timeout=10
        )

        # Get changed file names
        files_result = subprocess.run(
            ['git', 'diff', '--name-only', base_branch, target_branch],
            cwd=repo_path, capture_output=True, text=True, timeout=10
        )

        changed_files = [f.strip() for f in files_result.stdout.strip().split('\n') if f.strip()]

        diff_text = diff_result.stdout
        if len(diff_text) > 100_000:  # 100KB limit
            diff_text = diff_text[:100_000] + "\n\n... [diff truncated at 100KB] ..."

        return {
            "success": True,
            "repo_path": repo_path,
            "base_branch": base_branch,
            "target_branch": target_branch,
            "changed_files": changed_files,
            "total_files_changed": len(changed_files),
            "stats": stat_result.stdout,
            "diff": diff_text,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Git command timed out. The diff may be too large."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting git diff: {str(e)}"
        }


def search_in_code(query: str, directory: str, file_pattern: Optional[str] = None) -> dict:
    """Search for a pattern in source code files within a directory.

    Use this tool to find related code, trace data flows, locate usages of
    a function, or find security-relevant patterns across a codebase.


    Args:
        query: The text or pattern to search for (e.g., 'password', 'eval(',
               'database connection', 'SECRET_KEY', 'admin').
        directory: The directory to search in.
        file_pattern: Optional file extension filter (e.g., '*.py', '*.java').

    Returns:
        dict: Contains matching files, line numbers, and code snippets.
    """
    try:
        directory = os.path.expanduser(directory)
        if not os.path.isdir(directory):
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }

        # Build grep command
        cmd = ['grep', '-rn', '--include', file_pattern or '*', '-I',
               '--color=never', '-l', query, directory]

        # First get matching files
        files_result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )

        # Then get matching lines with context
        cmd_context = ['grep', '-rn', '--include', file_pattern or '*', '-I',
                       '--color=never', '-C', '2', query, directory]

        context_result = subprocess.run(
            cmd_context, capture_output=True, text=True, timeout=30
        )

        matching_files = [
            os.path.relpath(f.strip(), directory)
            for f in files_result.stdout.strip().split('\n')
            if f.strip()
        ]

        context_output = context_result.stdout
        if len(context_output) > 50_000:
            context_output = context_output[:50_000] + "\n\n... [output truncated] ..."

        return {
            "success": True,
            "query": query,
            "directory": directory,
            "matching_files": matching_files,
            "total_matches": len(matching_files),
            "results_with_context": context_output,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Search timed out. Try a more specific query or directory."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error searching code: {str(e)}"
        }


def get_dependency_file(project_path: str) -> dict:
    """Automatically find and read dependency/manifest files in a project.

    Searches for package.json, requirements.txt, pom.xml, go.mod, Gemfile,
    Cargo.toml, etc. and returns their contents for analysis.

    Args:
        project_path: Root path of the project to scan for dependency files.

    Returns:
        dict: Contains the dependency files found and their contents.
    """
    try:
        project_path = os.path.expanduser(project_path)
        if not os.path.isdir(project_path):
            return {
                "success": False,
                "error": f"Directory not found: {project_path}"
            }

        manifest_patterns = [
            'package.json', 'package-lock.json', 'yarn.lock',
            'requirements.txt', 'Pipfile', 'poetry.lock', 'pyproject.toml', 'setup.cfg',
            'pom.xml', 'build.gradle', 'build.gradle.kts',
            'go.mod', 'go.sum',
            'Cargo.toml', 'Cargo.lock',
            'Gemfile', 'Gemfile.lock',
            'composer.json', 'composer.lock',
            'pubspec.yaml', 'pubspec.lock',
            'mix.exs', 'mix.lock',
        ]

        found_files = {}
        for root, dirs, files in os.walk(project_path):
            # Skip deep/irrelevant dirs
            depth = root.replace(project_path, '').count(os.sep)
            if depth > 2:
                continue
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '.git', '__pycache__', 'venv', '.venv',
                'vendor', 'target', 'build', 'dist'
            }]

            for f in files:
                if f in manifest_patterns:
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, project_path)
                    try:
                        with open(full_path, 'r', errors='replace') as fh:
                            content = fh.read()
                        if len(content) < 100_000:  # Skip huge lockfiles
                            found_files[rel_path] = {
                                "filename": f,
                                "path": rel_path,
                                "content": content,
                                "size": len(content)
                            }
                    except Exception:
                        pass

        return {
            "success": True,
            "project_path": project_path,
            "files_found": len(found_files),
            "manifest_files": found_files,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error scanning dependencies: {str(e)}"
        }


def get_recent_commits(repo_path: str, count: int = 10) -> dict:
    """Get recent git commit history for a repository.

    Useful for understanding recent changes, identifying who made changes,
    and getting context for the code review.

    Args:
        repo_path: Path to the git repository.
        count: Number of recent commits to retrieve (default: 10, max: 50).

    Returns:
        dict: Contains the recent commits with hashes, authors, dates, and messages.
    """
    try:
        repo_path = os.path.expanduser(repo_path)
        count = min(count, 50)

        result = subprocess.run(
            ['git', 'log', f'-{count}', '--pretty=format:%H|%an|%ae|%ad|%s',
             '--date=iso'],
            cwd=repo_path, capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Not a git repository or git error: {result.stderr}"
            }

        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                parts = line.split('|', 4)
                if len(parts) == 5:
                    commits.append({
                        "hash": parts[0][:8],
                        "full_hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })

        return {
            "success": True,
            "repo_path": repo_path,
            "total_commits": len(commits),
            "commits": commits
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting commits: {str(e)}"
        }
