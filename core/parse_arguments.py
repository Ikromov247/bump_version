import warnings
import argparse
from core.config_handler import parse_config_arguments


def parse_cli_arguments(
    args: argparse.Namespace,
) -> tuple[list, bool, bool, bool, bool]:
    """
    Parse command line arguments from argparse.Namespace object
    Args:
        args(argparse.Namespace):
    Returns:
        tuple(list, bool, bool, bool, bool):
        tuple containing parsed arguments with file names and bump type flags
    """
    if not args.file:
        raise ValueError(
            f"At least one file path must be provided when not using a config file"
        )
    return args.file, args.major, args.minor, args.patch, args.git


def parse_arguments(args: argparse.Namespace) -> tuple[list, bool, bool, bool, bool]:
    """
    Wrapper function to parse arguments from various sources.
    Args:
        args(argparse.Namespace):
    Returns:
        tuple(list, bool, bool, bool, bool):
        tuple containing parsed arguments with file names and bump type flags
    Raises
        FileNotFoundError: if config path is given but file not found
    """
    # check if config is given
    if args.config:
        if args.file or args.minor or args.patch or args.git:
            warnings.warn(
                "Only one of config file or \
                        cli arguments are needed. Ignoring cli arguments."
            )
        return parse_config_arguments(args.config)

    ## if config is not given, use arguments
    else:
        return parse_cli_arguments(args)
