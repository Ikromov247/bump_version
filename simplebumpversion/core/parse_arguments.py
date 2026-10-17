import warnings
import argparse
from dataclasses import dataclass
from typing import List
from simplebumpversion.core.config_handler import parse_config_arguments
from simplebumpversion.core.exceptions import ArgumentsNotFound

DEFAULT_CHANGELOG = "CHANGELOG.md"


@dataclass
class BumpSettings:
    files: List[str]
    is_major: bool
    is_minor: bool
    is_patch: bool
    is_dry_run: bool
    changelog: str

    @property
    def update_type(self) -> str:
        if self.is_major:
            return "major"
        if self.is_minor:
            return "minor"
        return "patch"


def parse_cli_arguments(args: argparse.Namespace) -> BumpSettings:
    """
    Parse command line arguments from argparse.Namespace object
    Args:
        args(argparse.Namespace):
    Returns:
        BumpSettings: file names, bump type flags and run options
    Raises:
        ArgumentsNotFound: no file path was given
    """
    if not args.file:
        raise ArgumentsNotFound(
            "At least one file path must be provided when not using a config file"
        )
    return BumpSettings(
        files=args.file,
        is_major=args.major,
        is_minor=args.minor,
        is_patch=args.patch,
        is_dry_run=args.dry_run,
        changelog=args.changelog or DEFAULT_CHANGELOG,
    )


def parse_arguments(args: argparse.Namespace) -> BumpSettings:
    """
    Wrapper function to parse arguments from various sources.
    The config file replaces the files and bump type given in the CLI;
    run options such as --dry-run still apply.
    Args:
        args(argparse.Namespace):
    Returns:
        BumpSettings: file names, bump type flags and run options
    Raises
        FileNotFoundError: if config path is given but file not found
    """
    # check if config is given
    if args.config:
        if args.file or args.major or args.minor or args.patch:
            warnings.warn(
                "Only one of config file or cli arguments are needed. "
                "Ignoring files and bump type given in cli."
            )
        files, is_major, is_minor, is_patch, changelog = parse_config_arguments(
            args.config
        )
        return BumpSettings(
            files=files,
            is_major=is_major,
            is_minor=is_minor,
            is_patch=is_patch,
            is_dry_run=args.dry_run,
            changelog=changelog or args.changelog or DEFAULT_CHANGELOG,
        )

    ## if config is not given, use arguments
    else:
        return parse_cli_arguments(args)
