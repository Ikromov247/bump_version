#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
from typing import Optional, Tuple
from sys import exit
import yaml
import warnings

config_name_key = 'name'
config_desc_key = 'description'
settings_key = 'settings'
bump_type_key = 'bump_type'
files_key = 'files'

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
    major: bool = False,
    minor: bool = False,
    patch: bool = False,
    git_version: bool = False,
) -> str:
    """Bump the version according to the specified flags."""
    if git_version:
        return get_git_version()

    major_num, minor_num, patch_num = parse_version(current_version)

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

def parse_config_file(config_path: os.PathLike)->dict:
    """
    Open a yaml configuration file and return as a dict
    Args:
        config_path: os.PathLike
    Returns:
        dict
        app config in dict structure
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file {config_path} was not found")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def validate_config(config: dict)->bool:
    """
    Checks if the config dict contains 
    all required fields in the expected format
    Returns:
        bool
    """
    return True

def parse_arguments(args: argparse.Namespace)->tuple[list, bool, bool, bool]:
    # check if config is given
    if args.config:
        ## if yes, use config
        config = parse_config_file(args.config )
        ### if config not complete, raise error
        if not validate_config(config):
            raise ValueError("Config file is invalid")
        ### if other settings are given with config, raise warning and keep using config
        if args.file or args.minor or args.patch or args.git:
            warnings.warn("Only one of config file or \
                           cli arguments are needed. Ignoring cli arguments.")
        bump_type = config[settings_key][bump_type_key]
        if bump_type=='major':
            raise ValueError("Major version bumping is not supported with a config file. Use CLI instead")
        is_minor, is_patch, is_git = set_bump_type(bump_type)
        is_major = False
        files = config[settings_key][files_key]

        return files, is_major, is_minor, is_patch, is_git

    ## if config is not given, use arguments
    else:
        ### if arguments not complete, raise error
        if not args.file:
            raise ValueError(f"At least one file path must be provided when not using a config file")
        return args.file, args.major, args.minor, args.patch, args.git

def set_bump_type(bump_type):
    """
    Convert string bump type to boolean flags
    """
    is_minor = False
    is_patch = False
    is_git = False
    
    if bump_type == 'minor':
        is_minor = True
    elif bump_type == 'patch': 
        is_patch = True
    elif bump_type == 'git':
        is_git = True
    else:
        # Default to patch if unrecognized
        is_patch = True
    
    return is_minor, is_patch, is_git

def main():
    parser = argparse.ArgumentParser(description="Bump version in a file")
    parser.add_argument("file", nargs='*', help="Path to the file(s) containing version")
    parser.add_argument("--major", action="store_true", help="Bump major version")
    parser.add_argument("--minor", action="store_true", help="Bump minor version")
    parser.add_argument("--patch", action="store_true", help="Bump patch version")
    parser.add_argument("--git", action="store_true", help="Use git tag as version")
    parser.add_argument("--config", help="Load settings from a config file. Overrides cli arguments")

    args = parser.parse_args()

    target_files, is_major, is_minor, is_patch, is_git =  parse_arguments(args) # raises FileNotFoundError if config path is given but file not found

    # iterate the target files, check if they exist
    for file in target_files:
        # if yes, bump their version
        if not os.path.exists(file):
            print(f"Error: File '{file}' not found")
            return 1

        current_version = find_version_in_file(file)
        if not current_version:
            raise ValueError(f"Error: No version found in '{file}'")

        new_version = bump_version(
            current_version,
            major=is_major,
            minor=is_minor,
            patch=is_patch,
            git_version=is_git,
        )

        if update_version_in_file(file, current_version, new_version):
            print(f"Version bumped from {current_version} to {new_version}")
        else:
            print(f"Error: Failed to update version in '{file}'")

if __name__ == "__main__":
    exit(main())
