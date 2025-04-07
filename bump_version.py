#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
from typing import Optional, Tuple
from sys import exit


def get_git_version() -> str:
    """Get the current git version from the repository."""
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
        # If there are no tags yet, return a default version
        return "0.0.0"


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse a semantic version string into its components."""
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")

    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def bump_version(
    current_version: str,
    minor: bool = False,
    patch: bool = False,
    git_version: bool = False,
) -> str:
    """Bump the version according to the specified flags."""
    if git_version:
        return get_git_version()

    major_num, minor_num, patch_num = parse_version(current_version)

    if minor:
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

def parse_config_file(config_path: os.PathLike):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file {config_path} was not found")
    
    pass

def parse_arguments(args: argparse.Namespace):
    # check if config is given
    if args.config:
        config_path = args.config
        config = parse_config_file(config_path)
    ## if yes, use config
    ### if other settings are given with config, raise warning and keep using config
    ### if config not complete, raise error

    ## if config is not given, use arguments
    ### if arguments not complete, raise error

    return # files, version bump type


def main():
    parser = argparse.ArgumentParser(description="Bump version in a file")
    parser.add_argument("file", help="Path to the file containing version")
    parser.add_argument("--minor", action="store_true", help="Bump minor version")
    parser.add_argument("--patch", action="store_true", help="Bump patch version")
    parser.add_argument("--git", action="store_true", help="Use git tag as version")
    parser.add_argument("--config", help="Load settings from a config file")

    args = parser.parse_args()

    target_files, bump_type =  parse_arguments(args) # raises FileNotFoundError if config path is given but file not found
    # Default to patch bump if no specific bump type is provided
    if not any([args.minor, args.patch, args.git]):
        args.patch = True

    # iteratie the target files, check if they exist
    # if yes, bump their version
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        return 1

    current_version = find_version_in_file(args.file)
    if not current_version:
        print(f"Error: No version found in '{args.file}'")
        return 1

    new_version = bump_version(
        current_version,
        minor=args.minor,
        patch=args.patch,
        git_version=args.git,
    )

    if update_version_in_file(args.file, current_version, new_version):
        print(f"Version bumped from {current_version} to {new_version}")
        return 0
    else:
        print(f"Error: Failed to update version in '{args.file}'")
        return 1


if __name__ == "__main__":
    exit(main())
