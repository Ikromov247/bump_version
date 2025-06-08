import os
from datetime import datetime
import subprocess
import re


def write_changelog(new_version, changelog_path, message, update_type):
    new_entry = f"## {new_version} - {datetime.now().strftime('%Y-%m-%d')} [ {update_type} ]\n\n"
    new_entry += "\n".join(f"- {line}" for line in message.strip().splitlines())
    new_entry += "\n\n"

    if os.path.exists(changelog_path):
        with open(changelog_path, "r") as f:
            old_content = f.read()
    else:
        old_content = ""

    with open(changelog_path, "w") as f:
        f.write(new_entry + old_content)
