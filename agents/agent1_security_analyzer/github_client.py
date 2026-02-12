import base64
from typing import List, Dict, Any, Union
from github import Github, Repository, PullRequest

def create_client(token: str) -> Github:
    """
    Create an authenticated GitHub instance.
    """
    return Github(token)

def get_pr_files(client: Github, owner: str, repo_name: str, pr_number: int) -> List[Dict[str, str]]:
    """
    Fetch the list of files changed in a Pull Request.
    """
    repo = client.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)
    
    files = []
    # PyGithub paginates automatically
    for file in pr.get_files():
        files.append({
            "filename": file.filename,
            "status": file.status,
            "patch": file.patch if file.patch else "",
            "raw_url": file.raw_url
        })
    
    return files

def get_file_content(client: Github, owner: str, repo_name: str, path: str, ref: str) -> str:
    """
    Fetch raw file content from the repo at a given ref.
    """
    repo = client.get_repo(f"{owner}/{repo_name}")
    try:
        content_file = repo.get_contents(path, ref=ref)
        if isinstance(content_file, list):
            # If path points to a directory, we can't read it as a file
            raise ValueError(f"{path} is a directory")
            
        file_content = content_file.content
        if file_content:
            return base64.b64decode(file_content).decode('utf-8')
        return ""
        
    except Exception as e:
        print(f"Error fetching {path}: {e}")
        return ""

def post_pr_comment(client: Github, owner: str, repo_name: str, pr_number: int, body: str):
    """
    Post a comment on a Pull Request.
    """
    repo = client.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(body)
