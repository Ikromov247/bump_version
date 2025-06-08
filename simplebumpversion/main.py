import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simplebumpversion.core.parse_arguments import parse_arguments
from simplebumpversion.core.bump_version import (
    find_version_in_file,
    bump_semantic_version,
    update_version_in_file,
)
from simplebumpversion.core.exceptions import NoValidVersionStr
from simplebumpversion.core.git_tools import (
    get_latest_git_tag,
    get_commits_since_tag,
    update_git_tag,
    if_any_updates,
)
from simplebumpversion.core.change_logger import write_changelog


def main():
    parser = argparse.ArgumentParser(description="Bump version in a file")
    parser.add_argument(
        "file", nargs="*", help="Path to the file(s) containing version"
    )
    parser.add_argument("--major", action="store_true", help="Bump major version")
    parser.add_argument("--minor", action="store_true", help="Bump minor version")
    parser.add_argument("--patch", action="store_true", help="Bump patch version")

    parser.add_argument(
        "--config", help="Load settings from a config file. Overrides cli arguments"
    )

    parser.add_argument(
        "--change_msg", help="Change description string (can be multiline)"
    )

    parser.add_argument(
        "--change_msg_file", help="Path to file containing changelog message"
    )

    parser.add_argument(
        "--changelog", default="CHANGELOG.md", help="Path to changelog file"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Doesn't change the version file, prints what will happen",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        # print help message when no args are provided
        parser.print_help(sys.stderr)
        sys.exit(1)

    target_files, is_major, is_minor, is_patch, is_dry_run = parse_arguments(args)

    if is_dry_run:
        print("# DRY RUN MODE - no changes will be made")

    # iterate the target files, check if they exist
    for file in target_files:
        # if yes, bump their version
        if not os.path.exists(file):
            print(f"Error: File '{file}' not found")
            return 1

        try:
            current_version = find_version_in_file(file)

            try:
                if not if_any_updates():
                    print("No Updates since last version!")
                    return
                new_version = bump_semantic_version(
                    current_version, major=is_major, minor=is_minor, patch=is_patch
                )
                if is_major:
                    update_type = "major"
                elif is_minor:
                    update_type = "minor"
                elif is_patch:
                    update_type = "patch"
                else:
                    update_type = None

                updated = update_version_in_file(
                    file, current_version, new_version, is_dry_run
                )

                if updated:
                    print(f"Version bumped from {current_version} to {new_version}")
                    tag = get_latest_git_tag()
                    msg = get_commits_since_tag(tag)
                    if args.change_msg_file:
                        print("Using message from --change_msg_file")
                        try:
                            with open(args.change_msg_file, "r") as f:
                                msg = f.read().strip()
                        except FileNotFoundError:
                            print(f"Error: File '{args.change_msg_file}' not found.")
                            return 1
                    elif args.change_msg:
                        print("Using message from --change_msg")
                        msg = args.change_msg.strip()

                    # Only write changelog if message exists
                    change_log_file = (
                        args.changelog if args.changelog else "CHANGELOG.md"
                    )
                    if msg:
                        changelog_message = write_changelog(
                            new_version,
                            change_log_file or "CHANGELOG.md",
                            msg,
                            update_type,
                            is_dry_run,
                        )
                        print(f"Changelog updated with: \n {changelog_message}")
                    if not is_dry_run:
                        update_git_tag(new_version)
                else:
                    print(f"Error: Failed to update version in '{file}'")
                    return 1

            except ValueError as e:
                print(f"Error: {str(e)}")
                return 1

        except NoValidVersionStr as e:
            print(f"{str(e)}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
