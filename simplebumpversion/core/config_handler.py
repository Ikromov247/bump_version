import os
import yaml

config_name_key = "name"
config_desc_key = "description"
settings_key = "settings"
bump_type_key = "bump_type"
files_key = "files"
force_key = "force"


def open_config_file(config_path: os.PathLike) -> dict:
    """
    Open a yaml configuration file and return as a dict
    Args:
        config_path(os.PathLike): path to config file
    Returns:
        dict: app config in dict structure
    Raises:
        FileNotFoundError: config file is not found
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file {config_path} was not found")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def validate_config(config: dict) -> bool:
    """
    Checks if the config dict contains
    all required fields in the expected format
    Returns:
        bool
    """
    return True


def parse_config_arguments(
    config_path: os.PathLike,
) -> tuple[list[str], bool, bool, bool, bool, bool]:
    """
    Parse the arguments in the config file
    Args:
        config(os.PathLike): path to the config file
    Returns:
        tuple(list[str], bool, bool, bool, bool):
        list of paths to files with version numbers and boolean flags for bump version type
    Raises:
        ValueError: config file is invalid
        ValueError: major bump type provided in config file
    """
    config = open_config_file(config_path)
    ### if config not complete, raise error
    if not validate_config(config):
        raise ValueError("Config file is invalid")
    bump_type: str = config[settings_key][bump_type_key]
    if bump_type == "major":
        raise ValueError(
            "Major version bumping is not supported with a config file. Use CLI instead"
        )
    is_minor, is_patch, is_git = get_bump_flags(bump_type)
    is_major = False
    files = config[settings_key][files_key]
    # Check if force flag is provided in config
    is_force = False
    if force_key in config[settings_key]:
        is_force = bool(config[settings_key][force_key])
    return files, is_major, is_minor, is_patch, is_git, is_force


def get_bump_flags(bump_type: str) -> list[bool, bool, bool]:
    """
    Convert string bump type to boolean flags.
    If the version type is not recognized, set to patch
    Args:
        bump_type(str): bump type (major, minor, patch)
    Returns:
        list(bool, bool, bool):
        List of boolean flags. Only one is true
    """
    is_minor = False
    is_patch = False
    is_git = False

    if bump_type == "minor":
        is_minor = True
    elif bump_type == "patch":
        is_patch = True
    elif bump_type == "git":
        is_git = True
    else:
        # Default to patch if unrecognized
        is_patch = True

    return is_minor, is_patch, is_git
