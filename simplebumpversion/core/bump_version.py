#!/usr/bin/env python3
import re
from typing import Optional, Tuple
from simplebumpversion.core.git_tools import get_git_version
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


def bump_semantic_version(
    current_version: str,
    major: bool = False,
    minor: bool = False,
    patch: bool = False,
    git_version: bool = False,
) -> str:
    """
    Bump the version according to the specified flags.
    Args:
        current_version(str): the current version as str, e.g. version=1.2.3
        major(bool):
        minor(bool):
        patch(bool):
        git_version(bool):
    Returns:
        str: upgraded version as string, e.g. 1.2.4
    """
    if git_version:
        return get_git_version()

    major_num, minor_num, patch_num = parse_semantic_version(current_version)

    if major:
        major_num += 1
        minor_num = 1
        patch_num = 0
    elif minor:
        minor_num += 1
        patch_num = 0
    elif patch:
        patch_num += 1
    else:  # update patch number if all flags are false
        patch_num += 1

    return f"{major_num}.{minor_num}.{patch_num}"


def find_version_in_file(file_path: str) -> Optional[str]:
    """
    Find the version string in the specified file.
    Args:
        file_path(str): Path to the file containing the version number.
    Returns:
        str|None: version number string or None
    Raises:
        ValueError: version number pattern is not found in the file
    """
    content = read_file(file_path)

    # Common version patterns
    patterns = [
        r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # version = "1.2.3"
        r'VERSION\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # VERSION = "1.2.3"
        r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # __version__ = "1.2.3"
        r'"version"\s*:\s*"(\d+\.\d+\.\d+)"',  # "version": "1.2.3"
    ]
    version = None
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            version = match.group(1)
            break

    if version is None:
        raise NoValidVersionStr(f"Error: No version found in {file_path}")

    return version


def update_version_in_file(file_path: str, old_version: str, new_version: str) -> bool:
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

    # Common version patterns to replace
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

    if updated:
        write_to_file(file_path, content)
    return updated
