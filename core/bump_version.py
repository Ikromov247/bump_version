#!/usr/bin/env python3
import re
from typing import Optional, Tuple
from core.git_tools import get_git_version

def parse_semantic_version(version_str: str) -> Tuple[int, int, int]:
    """Parse a semantic version string into its integer components."""
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
    """Bump the version according to the specified flags."""
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

    return f"{major_num}.{minor_num}.{patch_num}"


def find_version_in_file(file_path: str) -> Optional[str]:
    """Find the version string in the specified file."""
    with open(file_path, "r") as f:
        content = f.read()

    # Common version patterns
    patterns = [
        r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # version = "1.2.3"
        r'VERSION\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # VERSION = "1.2.3"
        r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # __version__ = "1.2.3"
        r'"version"\s*:\s*"(\d+\.\d+\.\d+)"',  # "version": "1.2.3"
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1)

    return None


def update_version_in_file(file_path: str, old_version: str, new_version: str) -> bool:
    """Update the version in the specified file."""
    with open(file_path, "r") as f:
        content = f.read()

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
        with open(file_path, "w") as f:
            f.write(content)

    return updated


