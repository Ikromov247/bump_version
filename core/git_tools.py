import subprocess


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
        # Get the most recent tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=1"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        raise ValueError("Error occured when reading the git tag")
