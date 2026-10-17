import os
import sys
import argparse
from typing import List, Optional

from simplebumpversion.core.parse_arguments import parse_arguments
from simplebumpversion.core.bump_version import (
    find_version_in_file,
    bump_semantic_version,
    replace_version,
)
from simplebumpversion.core.exceptions import ArgumentsNotFound, NoValidVersionStr
from simplebumpversion.core.file_handler import read_file, write_to_file
from simplebumpversion.core.git_tools import (
    GitError,
    get_latest_git_tag,
    get_commits_since_tag,
    tag_exists,
    commit_files,
    update_git_tag,
)
from simplebumpversion.core.change_logger import write_changelog


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bump version in a file")
    parser.add_argument(
        "file", nargs="*", help="Path to the file(s) containing version"
    )
    bump_type = parser.add_mutually_exclusive_group()
    bump_type.add_argument("--major", action="store_true", help="Bump major version")
    bump_type.add_argument("--minor", action="store_true", help="Bump minor version")
    bump_type.add_argument("--patch", action="store_true", help="Bump patch version")

    parser.add_argument(
        "--config",
        help="Load files and bump type from a config file. Overrides cli arguments",
    )

    parser.add_argument(
        "--change_msg", help="Change description string (can be multiline)"
    )

    parser.add_argument(
        "--change_msg_file", help="Path to file containing changelog message"
    )

    parser.add_argument(
        "--changelog",
        default=None,
        help="Path to changelog file (default: change_log_file from config, or CHANGELOG.md)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Doesn't change the version file, prints what will happen",
    )

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit the changed files and tag the new commit with the new version",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Bump even if there are no new commits since the last tag",
    )
    return parser


def set_github_output(**outputs: str) -> None:
    """Expose results as step outputs when running inside GitHub Actions."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return
    with open(output_file, "a", encoding="utf-8") as f:
        for key, value in outputs.items():
            f.write(f"{key}={value}\n")


def get_change_message(args: argparse.Namespace, tag: Optional[str]) -> Optional[str]:
    if args.change_msg_file:
        print("Using message from --change_msg_file")
        return read_file(args.change_msg_file).strip()
    if args.change_msg:
        print("Using message from --change_msg")
        return args.change_msg.strip()
    return get_commits_since_tag(tag)


def run(args: argparse.Namespace) -> int:
    settings = parse_arguments(args)

    if settings.is_dry_run:
        print("# DRY RUN MODE - no changes will be made")

    # check every file before changing any of them
    for file in settings.files:
        if not os.path.isfile(file):
            print(f"Error: File '{file}' not found", file=sys.stderr)
            return 1

    versions = {file: find_version_in_file(file) for file in settings.files}
    if len(set(versions.values())) > 1:
        found = ", ".join(f"{file}: {version}" for file, version in versions.items())
        raise ValueError(f"Files contain different versions ({found})")
    current_version = versions[settings.files[0]]

    last_tag = get_latest_git_tag()
    if not get_commits_since_tag(last_tag) and not args.force:
        print("No updates since last version! Use --force to bump anyway.")
        set_github_output(bumped="false", previous_version=current_version)
        return 0

    new_version = bump_semantic_version(
        current_version,
        major=settings.is_major,
        minor=settings.is_minor,
        patch=settings.is_patch,
    )
    if args.commit and tag_exists(new_version):
        raise ValueError(f"Git tag '{new_version}' already exists")

    msg = get_change_message(args, last_tag)

    new_contents = {}
    for file in settings.files:
        content, updated = replace_version(
            read_file(file), current_version, new_version
        )
        if not updated:
            raise ValueError(f"Failed to update version in '{file}'")
        new_contents[file] = content

    if not settings.is_dry_run:
        for file, content in new_contents.items():
            write_to_file(file, content)
    print(f"Version bumped from {current_version} to {new_version}")

    changed_files: List[str] = list(settings.files)
    # Only write changelog if message exists
    if msg:
        changelog_message = write_changelog(
            new_version,
            settings.changelog,
            msg,
            settings.update_type,
            settings.is_dry_run,
        )
        print(f"Changelog updated with: \n {changelog_message}")
        changed_files.append(settings.changelog)

    if settings.is_dry_run:
        set_github_output(
            bumped="false",
            previous_version=current_version,
            new_version=new_version,
        )
        return 0

    if args.commit:
        commit_files(changed_files, f"Bump version to {new_version} [skip ci]")
        update_git_tag(new_version)
    else:
        print("Changes are not committed or tagged. Use --commit to do both.")

    set_github_output(
        bumped="true", previous_version=current_version, new_version=new_version
    )
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        # print help message when no args are provided
        parser.print_help(sys.stderr)
        return 1

    args = parser.parse_args(argv)
    try:
        return run(args)
    except (ArgumentsNotFound, NoValidVersionStr, GitError, ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
