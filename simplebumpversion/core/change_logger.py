import os
from datetime import datetime
from simplebumpversion.core.file_handler import read_file, write_to_file


def write_changelog(new_version, changelog_path, message, update_type, is_dry_run):
    new_entry = f"## {new_version} - {datetime.now().strftime('%Y-%m-%d')} [ {update_type} ]\n\n"
    new_entry += "\n".join(f"- {line}" for line in message.strip().splitlines())
    new_entry += "\n\n"

    if os.path.exists(changelog_path):
        old_content = read_file(changelog_path)
    else:
        old_content = ""

    if not is_dry_run:
        write_to_file(changelog_path, new_entry + old_content)

    return new_entry
