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
            ["git", "describe", "--tags", "--abbrev=0"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        raise ValueError("Error occured when reading the git tag")


def update_git_tag(new_version, msg=None):
    try:
        if msg is not None:
            subprocess.run(["git", "tag", "-a", new_version, "-m", msg], check=True)
        else:
            subprocess.run(
                ["git", "tag", "-a", new_version, "-m", f"Tag {new_version}"],
                check=True,
            )
        print(f"Tag '{new_version}' created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to create git tag '{new_version}'.")
        print(e)


def get_latest_git_tag():
    try:
        return (
            subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        return None


def get_commits_since_tag(tag):
    try:
        log_range = f"{tag}..HEAD" if tag else "HEAD"
        output = (
            subprocess.check_output(["git", "log", log_range, "--oneline"])
            .decode()
            .strip()
        )
        commits = output.splitlines()
        result = "\n".join(commits) if commits else None
        return result
    except subprocess.CalledProcessError:
        print("Error while fetching commits since last tag")


def if_any_updates():
    last_tag = get_latest_git_tag()
    commits = get_commits_since_tag(last_tag)
    return True if commits else False


if __name__ == "__main__":
    # tag = get_git_version()
    tag = get_latest_git_tag()
    print("Last tag:", tag)

    commits = get_commits_since_tag(tag)
    print("Commits since tag:", commits)
