#!/usr/bin/env python3
import re
from typing import Optional, Tuple
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
    match = re.fullmatch(
        r"v?(\d+)\.(\d+)\.(\d+)", version_str
    )  # supports both 1.2.3 and v.1.2.3 formats
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
    has_v_prefix = current_version.startswith("v")
    # Normal semantic version handling
    try:
        major_num, minor_num, patch_num = parse_semantic_version(current_version)
    except ValueError:
        raise ValueError(
            f"Cannot bump version: '{current_version}' is not a valid semantic version (e.g. '1.2.3')"
        )

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

    bumped_version = f"{major_num}.{minor_num}.{patch_num}"
    return f"v{bumped_version}" if has_v_prefix else bumped_version


# Each pattern captures (prefix)(version)(suffix). The lookbehind stops
# keys such as "target-version" or "python_version" from matching.
_VERSION_KEY_PATTERNS = [
    r"((?<![\w.\-])version\s*=\s*[\"'])({version})([\"'])",  # version = "1.2.3"
    r"((?<![\w.\-])VERSION\s*=\s*[\"'])({version})([\"'])",  # VERSION = "1.2.3"
    r"((?<![\w.\-])__version__\s*=\s*[\"'])({version})([\"'])",  # __version__ = "1.2.3"
    r'("version"\s*:\s*")({version})(")',  # "version": "1.2.3"
]

# strict semantic versions are preferred over anything else
_SEMANTIC_VERSION = r"v?\d+\.\d+\.\d+"
# more flexible format that can match git tags, e.g. v1.2.3-19-gabc123
_FLEXIBLE_VERSION = r"[\w.\-]+"


def find_version_in_file(file_path: str) -> str:
    """
    Find the version string in the specified file.
    Args:
        file_path(str): Path to the file containing the version number.
    Returns:
        str: version number string
    Raises:
        NoValidVersionStr: version number pattern is not found in the file
    """
    content = read_file(file_path)

    for version_pattern in (_SEMANTIC_VERSION, _FLEXIBLE_VERSION):
        for pattern in _VERSION_KEY_PATTERNS:
            match = re.search(pattern.format(version=version_pattern), content)
            if match:
                return match.group(2)

    raise NoValidVersionStr(f"No version found in {file_path}")


def replace_version(
    content: str, old_version: str, new_version: str
) -> Tuple[str, bool]:
    """
    Replace the first occurrence of old_version in a version assignment,
    keeping the original quoting and spacing.
    Args:
        content(str): file content
        old_version(str): old version number string
        new_version(str): the new version number string
    Returns:
        tuple(str, bool): updated content and whether a replacement was made
    """
    for pattern in _VERSION_KEY_PATTERNS:
        match = re.search(pattern.format(version=re.escape(old_version)), content)
        if match:
            start, end = match.span(2)
            return content[:start] + new_version + content[end:], True
    return content, False


def update_version_in_file(
    file_path: str, old_version: str, new_version: str, is_dry_run: bool
) -> bool:
    """
    Update the version in the specified file.
    Args:
        file_path(str): path to the file to update
        old_version(str): old version number string
        new_version(str): the new version number string
        is_dry_run(bool): don't write the changes if True
    Returns:
        bool: whether version update was successful
    """
    content, updated = replace_version(read_file(file_path), old_version, new_version)
    if updated and not is_dry_run:
        write_to_file(file_path, content)
    return updated
