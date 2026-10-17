import os
from typing import List, Optional, Tuple
import yaml

config_name_key = "name"
config_desc_key = "description"
settings_key = "settings"
bump_type_key = "bump_type"
files_key = "files"

change_log_file_key = "change_log_file"

valid_bump_types = ("major", "minor", "patch")


def open_config_file(config_path: os.PathLike) -> dict:
    """
    Open a yaml configuration file and return as a dict
    Args:
        config_path(os.PathLike): path to config file
    Returns:
        dict: app config in dict structure
    Raises:
        FileNotFoundError: config file is not found
        ValueError: config file is not valid YAML
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file {config_path} was not found")
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Config file {config_path} is not valid YAML: {e}")
    return config


def write_config_file(config_path, config):
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False)


def validate_config(config: dict) -> None:
    """
    Checks if the config dict contains
    all required fields in the expected format
    Raises:
        ValueError: config is missing a field or a field has the wrong type
    """
    if not isinstance(config, dict) or not isinstance(config.get(settings_key), dict):
        raise ValueError(f"Config file is invalid: missing '{settings_key}' section")
    settings = config[settings_key]

    files = settings.get(files_key)
    if isinstance(files, str):
        files = [files]
    if (
        not isinstance(files, list)
        or not files
        or not all(isinstance(f, str) and f for f in files)
    ):
        raise ValueError(
            f"Config file is invalid: '{settings_key}.{files_key}' must be a non-empty list of file paths"
        )

    bump_type = settings.get(bump_type_key, "patch")
    if bump_type not in valid_bump_types:
        raise ValueError(
            f"Config file is invalid: unknown {bump_type_key} '{bump_type}', expected one of {', '.join(valid_bump_types)}"
        )

    change_log_file = settings.get(change_log_file_key)
    if change_log_file is not None and not isinstance(change_log_file, str):
        raise ValueError(
            f"Config file is invalid: '{settings_key}.{change_log_file_key}' must be a file path"
        )


def parse_config_arguments(
    config_path: os.PathLike,
) -> Tuple[List[str], bool, bool, bool, Optional[str]]:
    """
    Parse the arguments in the config file
    Args:
        config(os.PathLike): path to the config file
    Returns:
        tuple(list[str], bool, bool, bool, str|None):
        list of paths to files with version numbers, boolean flags for bump version type
        and the changelog file path, if set
    Raises:
        ValueError: config file is invalid
        ValueError: major bump type provided in config file
    """
    config = open_config_file(config_path)
    validate_config(config)
    settings = config[settings_key]

    bump_type: str = settings.get(bump_type_key, "patch")
    if bump_type == "major":
        raise ValueError(
            "Major version bumping is not supported with a config file. Use CLI instead"
        )
    is_minor, is_patch = get_bump_flags(bump_type)
    is_major = False

    files = settings[files_key]
    if isinstance(files, str):
        files = [files]

    return files, is_major, is_minor, is_patch, settings.get(change_log_file_key)


def get_bump_flags(bump_type: str) -> Tuple[bool, bool]:
    """
    Convert string bump type to boolean flags.
    If the version type is not recognized, set to patch
    Args:
        bump_type(str): bump type (major, minor, patch)
    Returns:
        list(bool, bool):
        List of boolean flags. Only one is true
    """
    is_minor = False
    is_patch = False

    if bump_type == "minor":
        is_minor = True
    elif bump_type == "patch":
        is_patch = True
    else:
        # Default to patch if unrecognized
        is_patch = True

    return is_minor, is_patch


def get_change_log_file(config_path) -> Optional[str]:
    config = open_config_file(config_path)
    validate_config(config)
    return config[settings_key].get(change_log_file_key)


def set_change_log_file(config_path, new_name):
    config = open_config_file(config_path)
    validate_config(config)
    config[settings_key][change_log_file_key] = new_name
    write_config_file(config_path, config)
