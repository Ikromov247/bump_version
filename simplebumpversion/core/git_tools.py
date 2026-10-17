import subprocess
from typing import List, Optional


class GitError(Exception):
    """A git command failed"""


def _run_git(args: List[str]) -> str:
    """
    Run a git command and return its stripped stdout.
    Raises:
        GitError: git is missing or the command failed
    """
    try:
        result = subprocess.run(
            ["git", *args], check=True, capture_output=True, text=True
        )
    except FileNotFoundError:
        raise GitError("git executable was not found")
    except subprocess.CalledProcessError as e:
        details = (e.stderr or e.stdout or "").strip()
        raise GitError(f"'git {' '.join(args)}' failed: {details}")
    return result.stdout.strip()


def get_git_version() -> str:
    """
    Get the current git version from the repository.

    Returns:
        git tag
    Ex: v0.9-19-g7e2d, where
        - 'v0.9' is the tag
        - '19' is the commit order number (19th commit in the repo)
        - 'g7e2d' is the abbreviated hash of the last commit
    Raises:
        ValueError: git tag is not found locally
    """
    try:
        return _run_git(["describe", "--tags", "--abbrev=0"])
    except GitError:
        raise ValueError("Error occured when reading the git tag")


def get_latest_git_tag() -> Optional[str]:
    """
    Return the most recent tag reachable from HEAD, or None if there is none.
    """
    try:
        return _run_git(["describe", "--tags", "--abbrev=0"]) or None
    except GitError:
        return None


def tag_exists(tag: str) -> bool:
    return bool(_run_git(["tag", "--list", tag]))


def get_commits_since_tag(tag: Optional[str]) -> Optional[str]:
    """
    Return the one-line log of commits since the given tag (or all commits
    if tag is None). Automated "[skip ci]" commits, such as previous version
    bump commits, are left out.
    Raises:
        GitError: the log could not be read, e.g. not inside a git repository
    """
    log_range = f"{tag}..HEAD" if tag else "HEAD"
    output = _run_git(["log", log_range, "--oneline"])
    commits = [line for line in output.splitlines() if "[skip ci]" not in line]
    return "\n".join(commits) if commits else None


def if_any_updates() -> bool:
    last_tag = get_latest_git_tag()
    commits = get_commits_since_tag(last_tag)
    return True if commits else False


def commit_files(files: List[str], message: str) -> None:
    _run_git(["add", "--", *files])
    _run_git(["commit", "-m", message])


def update_git_tag(new_version: str, msg: Optional[str] = None) -> None:
    """
    Create an annotated tag on HEAD.
    Raises:
        GitError: the tag could not be created
    """
    _run_git(["tag", "-a", new_version, "-m", msg or f"Tag {new_version}"])
    print(f"Tag '{new_version}' created successfully.")


if __name__ == "__main__":
    tag = get_latest_git_tag()
    print("Last tag:", tag)

    commits = get_commits_since_tag(tag)
    print("Commits since tag:", commits)
