import os
import sys
import argparse

from simplebumpversion.core.parse_arguments import parse_arguments
from simplebumpversion.core.bump_version import (
    find_version_in_file,
    bump_semantic_version,
    update_version_in_file,
)


def main():
    parser = argparse.ArgumentParser(description="Bump version in a file")
    parser.add_argument(
        "file", nargs="*", help="Path to the file(s) containing version"
    )
    parser.add_argument("--major", action="store_true", help="Bump major version")
    parser.add_argument("--minor", action="store_true", help="Bump minor version")
    parser.add_argument("--patch", action="store_true", help="Bump patch version")
    parser.add_argument("--git", action="store_true", help="Use git tag as version")
    parser.add_argument(
        "--config", help="Load settings from a config file. Overrides cli arguments"
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        # print help message when no args are provided
        parser.print_help(sys.stderr)
        sys.exit(1)

    target_files, is_major, is_minor, is_patch, is_git = parse_arguments(args)

    # iterate the target files, check if they exist
    for file in target_files:
        # if yes, bump their version
        if not os.path.exists(file):
            print(f"Error: File '{file}' not found")
            return 1

        current_version = find_version_in_file(file)

        new_version = bump_semantic_version(
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
    sys.exit(main())
