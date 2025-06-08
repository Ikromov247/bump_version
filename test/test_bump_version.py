import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import re
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from simplebumpversion.core.bump_version import (
    parse_semantic_version,
    bump_semantic_version,
    find_version_in_file,
    update_version_in_file,
    is_git_tag_version,
)

from simplebumpversion.core.exceptions import NoValidVersionStr


class TestBumpVersion(unittest.TestCase):
    def test_parse_semantic_version(self):
        major, minor, patch = parse_semantic_version("1.2.3")
        self.assertEqual((major, minor, patch), (1, 2, 3))

        with self.assertRaises(ValueError):
            parse_semantic_version("not-a-version")

        with self.assertRaises(ValueError):
            parse_semantic_version("v1.2.3-19-g123abc")

    def test_bump_semantic_version(self):
        self.assertEqual(bump_semantic_version("1.2.3", patch=True), "1.2.4")
        self.assertEqual(bump_semantic_version("1.2.3", minor=True), "1.3.0")
        self.assertEqual(bump_semantic_version("1.2.3", major=True), "2.0.0")
        self.assertEqual(bump_semantic_version("1.2.3"), "1.2.4")

        self.assertEqual(bump_semantic_version("v1.2.3", patch=True), "v1.2.4")
        self.assertEqual(bump_semantic_version("v1.2.3", minor=True), "v1.3.0")
        self.assertEqual(bump_semantic_version("v1.2.3", major=True), "v2.0.0")
        self.assertEqual(bump_semantic_version("v1.2.3"), "v1.2.4")

        # Test invalid input
        with self.assertRaises(ValueError):
            bump_semantic_version("v1.2.3-19-g7e2d", patch=True)

    def test_is_git_tag_version(self):
        self.assertTrue(is_git_tag_version("v0.9-19-g7e2d"))
        self.assertTrue(is_git_tag_version("1.2.3-alpha"))
        self.assertFalse(is_git_tag_version("1.2.3"))
        self.assertTrue(is_git_tag_version("release-2023"))

    def test_find_version_in_file(self):
        with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp:
            tmp.write('__version__ = "1.2.3"\n')
            tmp.flush()
            found = find_version_in_file(tmp.name)
            self.assertEqual(found, "1.2.3")

        with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp:
            tmp.write('version = "v0.9-19-g7e2d"\n')
            tmp.flush()
            found = find_version_in_file(tmp.name)
            self.assertEqual(found, "v0.9-19-g7e2d")

        with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp:
            tmp.write("no version here\n")
            tmp.flush()
            with self.assertRaises(NoValidVersionStr):
                find_version_in_file(tmp.name)

    def test_update_version_in_file(self):
        with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp:
            tmp.write('__version__ = "1.2.3"\n')
            tmp.flush()
            updated = update_version_in_file(
                tmp.name, "1.2.3", "1.2.4", is_dry_run=False
            )
            self.assertTrue(updated)
            with open(tmp.name) as f:
                content = f.read()
            self.assertIn("1.2.4", content)

        with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp:
            tmp.write('version = "v0.9-19-g7e2d"\n')
            tmp.flush()
            updated = update_version_in_file(
                tmp.name, "v0.9-19-g7e2d", "1.0.0", is_dry_run=False
            )
            self.assertTrue(updated)
            with open(tmp.name) as f:
                content = f.read()
            self.assertIn("1.0.0", content)

        with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp:
            tmp.write('version = "1.2.3"\n')
            tmp.flush()
            updated = update_version_in_file(
                tmp.name, "9.9.9", "1.2.4", is_dry_run=False
            )
            self.assertFalse(updated)


if __name__ == "__main__":
    unittest.main()
