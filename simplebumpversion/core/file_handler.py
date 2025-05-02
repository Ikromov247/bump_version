"""
Helper module for reading and writing to generic files.
The main objective of this module is to allow code reuse and implement error handling in one place.
"""


def read_file(file_path: str) -> str:
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {file_path}")
    except PermissionError:
        raise PermissionError(f"Could not read {file_path}")


def write_to_file(file_path: str, content: str) -> None:
    try:
        with open(file_path, "w") as f:
            f.write(content)
    except PermissionError:
        raise PermissionError(f"Could not read {file_path}")
