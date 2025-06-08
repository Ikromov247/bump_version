#!/usr/bin/env python3
import re
from typing import Optional, Tuple
from simplebumpversion.core.git_tools import get_git_version, get_latest_git_tag
from simplebumpversion.core.file_handler import read_file, write_to_file
from simplebumpversion.core.exceptions import NoValidVersionStr


def parse_semantic_version(version_str: str) -> Tuple[int, int, int]:
    """
    Parse a semantic version string into its integer components.
    Args:
        version_str(str): a string containing the version number.
    Returns:
        tuple(int, int, int):
        Tuple containing major, minor and patch versions as int
    Raises:
        ValueError:
    """
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")

    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def is_git_tag_version(version_str: str) -> bool:
    """
    Check if a version string looks like a git tag.

    Git tag versions typically include hyphens, commit hashes, etc.
    Example: v0.9-19-g7e2d

    Args:
        version_str(str): The version string to check

    Returns:
        bool: True if it looks like a git tag, False otherwise
    """
    # Git tags often have this format: v0.9-19-g7e2d
    # They frequently contain hyphens and letters not in the semantic version pattern
    return "-" in version_str or (  # Contains hyphen
        not re.match(r"^\d+\.\d+\.\d+$", version_str)  # Not a simple semantic version
        and any(c.isalpha() for c in version_str)
    )  # Contains letters


def bump_semantic_version(
    current_version: str, major: bool = False, minor: bool = False, patch: bool = False
) -> str:
    """
    Bump the version according to the specified flags.
    Args:
        current_version(str): the current version as str, e.g. version=1.2.3
        major(bool): bump major version
        minor(bool): bump minor version
        patch(bool): bump patch version
    Returns:
        str: upgraded version as string, e.g. 1.2.4
    """
    # Normal semantic version handling
    major_num, minor_num, patch_num = parse_semantic_version(current_version)
    if major:
        major_num += 1
        minor_num = 0
        patch_num = 0
    elif minor:
        minor_num += 1
        patch_num = 0
    elif patch:
        patch_num += 1
    else:  # update patch number if all flags are false
        patch_num += 1

    return f"{major_num}.{minor_num}.{patch_num}"


def find_version_in_file(file_path: str) -> str:
    """
    Find the version string in the specified file.
    Args:
        file_path(str): Path to the file containing the version number.
    Returns:
        str|None: version number string or None
    Raises:
        NoValidVersionStr: version number pattern is not found in the file
    """
    content = read_file(file_path)

    # Common semantic version patterns (strict semantic versioning)
    semantic_patterns = [
        r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # version = "1.2.3"
        r'VERSION\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # VERSION = "1.2.3"
        r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # __version__ = "1.2.3"
        r'"version"\s*:\s*"(\d+\.\d+\.\d+)"',  # "version": "1.2.3"
    ]

    # More flexible patterns that can match git tags or other version formats
    flexible_patterns = [
        r'version\s*=\s*["\']([\w\.\-]+)["\']',  # version = "v1.2.3-19-gabc123"
        r'VERSION\s*=\s*["\']([\w\.\-]+)["\']',  # VERSION = "v1.2.3-19-gabc123"
        r'__version__\s*=\s*["\']([\w\.\-]+)["\']',  # __version__ = "v1.2.3-19-gabc123"
        r'"version"\s*:\s*"([\w\.\-]+)"',  # "version": "v1.2.3-19-gabc123"
    ]

    # First try to find a semantic version
    version = None
    for pattern in semantic_patterns:
        match = re.search(pattern, content)
        if match:
            version = match.group(1)
            break

    # If no semantic version found, try flexible patterns that can match git tags
    if version is None:
        for pattern in flexible_patterns:
            match = re.search(pattern, content)
            if match:
                version = match.group(1)
                break

    if version is None:
        raise NoValidVersionStr(f"Error: No version found in {file_path}")

    return version


def update_version_in_file(
    file_path: str, old_version: str, new_version: str, is_dry_run: bool
) -> bool:
    """
    Update the version in the specified file.
    Args:
        file_path(str): path to the file to update
        old_version(str): old version number string
        new_version(str): the new version number string
    Returns:
        bool: whether version update was successful
    """
    content = read_file(file_path)

    # Common version patterns to replace, works for both semantic versions and git tags
    patterns = [
        (
            f"version\\s*=\\s*[\"']({re.escape(old_version)})[\"']",
            f'version = "{new_version}"',
        ),
        (
            f"VERSION\\s*=\\s*[\"']({re.escape(old_version)})[\"']",
            f'VERSION = "{new_version}"',
        ),
        (
            f"__version__\\s*=\\s*[\"']({re.escape(old_version)})[\"']",
            f'__version__ = "{new_version}"',
        ),
        (
            f'"version"\\s*:\\s*"({re.escape(old_version)})"',
            f'"version": "{new_version}"',
        ),
    ]

    updated = False
    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            updated = True

    if updated and not is_dry_run:
        write_to_file(file_path, content)
    return updated
