"""
Helper module for reading and writing to generic files.
The main objective of this module is to allow code reuse and implement error handling in one place.
"""

import os
import shutil
import tempfile


def read_file(file_path: str) -> str:
    try:
        # newline="" keeps the original line endings intact
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {file_path}")
    except PermissionError:
        raise PermissionError(f"Could not read {file_path}")


def write_to_file(file_path: str, content: str) -> None:
    """
    Write content to a file atomically: the content is written to a temporary
    file in the same directory and then moved over the target, so a failure
    midway never leaves a half-written file behind.
    """
    directory = os.path.dirname(os.path.abspath(file_path))
    try:
        fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".bump-", suffix=".tmp")
    except PermissionError:
        raise PermissionError(f"Could not write to {file_path}")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        if os.path.exists(file_path):
            shutil.copymode(file_path, tmp_path)
        os.replace(tmp_path, file_path)
    except PermissionError:
        raise PermissionError(f"Could not write to {file_path}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
