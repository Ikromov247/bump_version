#!/usr/bin/env python3
import os
import unittest
from unittest.mock import patch, mock_open
import core.bump_version as bump_version


class TestBumpVersion(unittest.TestCase):
    def setUp(self):
        # Sample version string for testing
        self.version_content = 'version = "1.2.3"\n'

    @patch("os.path.exists")
    @patch("bump_version.find_version_in_file")
    @patch("bump_version.update_version_in_file")
    @patch("bump_version.argparse.ArgumentParser.parse_args")
    def test_main_patch_bump(self, mock_args, mock_update, mock_find, mock_exists):
        # Setup mocks
        mock_args.return_value = unittest.mock.Mock(
            file="test_file.py", minor=False, patch=True, git=False
        )
        mock_exists.return_value = True
        mock_find.return_value = "1.2.3"
        mock_update.return_value = True

        # Execute
        result = bump_version.main()

        # Assert
        mock_update.assert_called_once_with("test_file.py", "1.2.3", "1.2.4")
        self.assertEqual(result, 0)

    @patch("os.path.exists")
    @patch("bump_version.find_version_in_file")
    @patch("bump_version.update_version_in_file")
    @patch("bump_version.argparse.ArgumentParser.parse_args")
    def test_main_minor_bump(self, mock_args, mock_update, mock_find, mock_exists):
        # Setup mocks
        mock_args.return_value = unittest.mock.Mock(
            file="test_file.py", minor=True, patch=False, git=False
        )
        mock_exists.return_value = True
        mock_find.return_value = "1.2.3"
        mock_update.return_value = True

        # Execute
        result = bump_version.main()

        # Assert
        mock_update.assert_called_once_with("test_file.py", "1.2.3", "1.3.0")
        self.assertEqual(result, 0)

    @patch("os.path.exists")
    @patch("bump_version.find_version_in_file")
    @patch("bump_version.update_version_in_file")
    @patch("bump_version.argparse.ArgumentParser.parse_args")
    def test_main_default_to_patch(
        self, mock_args, mock_update, mock_find, mock_exists
    ):
        # Setup mocks
        mock_args.return_value = unittest.mock.Mock(
            file="test_file.py", minor=False, patch=False, git=False
        )
        mock_exists.return_value = True
        mock_find.return_value = "1.2.3"
        mock_update.return_value = True

        # Execute
        result = bump_version.main()

        # Assert
        mock_update.assert_called_once_with("test_file.py", "1.2.3", "1.2.4")
        self.assertEqual(result, 0)

    @patch("bump_version.get_git_version")
    @patch("os.path.exists")
    @patch("bump_version.find_version_in_file")
    @patch("bump_version.update_version_in_file")
    @patch("bump_version.argparse.ArgumentParser.parse_args")
    def test_main_git_version(
        self, mock_args, mock_update, mock_find, mock_exists, mock_git
    ):
        # Setup mocks
        mock_args.return_value = unittest.mock.Mock(
            file="test_file.py", minor=False, patch=False, git=True
        )
        mock_exists.return_value = True
        mock_find.return_value = "1.2.3"
        mock_git.return_value = "2.0.0"
        mock_update.return_value = True

        # Execute
        result = bump_version.main()

        # Assert
        mock_update.assert_called_once_with("test_file.py", "1.2.3", "2.0.0")
        self.assertEqual(result, 0)

    @patch("os.path.exists")
    @patch("bump_version.find_version_in_file")
    @patch("bump_version.update_version_in_file")
    @patch("bump_version.argparse.ArgumentParser.parse_args")
    def test_main_file_not_found(self, mock_args, mock_update, mock_find, mock_exists):
        # Setup mocks
        mock_args.return_value = unittest.mock.Mock(
            file="nonexistent_file.py", minor=False, patch=True, git=False
        )
        mock_exists.return_value = False

        # Execute
        result = bump_version.main()

        # Assert
        mock_find.assert_not_called()
        mock_update.assert_not_called()
        self.assertEqual(result, 1)

    @patch("os.path.exists")
    @patch("bump_version.find_version_in_file")
    @patch("bump_version.update_version_in_file")
    @patch("bump_version.argparse.ArgumentParser.parse_args")
    def test_main_no_version_found(
        self, mock_args, mock_update, mock_find, mock_exists
    ):
        # Setup mocks
        mock_args.return_value = unittest.mock.Mock(
            file="test_file.py", minor=False, patch=True, git=False
        )
        mock_exists.return_value = True
        mock_find.return_value = None

        # Execute
        result = bump_version.main()

        # Assert
        mock_update.assert_not_called()
        self.assertEqual(result, 1)

    @patch("os.path.exists")
    @patch("bump_version.find_version_in_file")
    @patch("bump_version.update_version_in_file")
    @patch("bump_version.argparse.ArgumentParser.parse_args")
    def test_main_update_failed(self, mock_args, mock_update, mock_find, mock_exists):
        # Setup mocks
        mock_args.return_value = unittest.mock.Mock(
            file="test_file.py", minor=False, patch=True, git=False
        )
        mock_exists.return_value = True
        mock_find.return_value = "1.2.3"
        mock_update.return_value = False

        # Execute
        result = bump_version.main()

        # Assert
        mock_update.assert_called_once_with("test_file.py", "1.2.3", "1.2.4")
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
