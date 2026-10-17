import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from simplebumpversion.main import main
from simplebumpversion.core.bump_version import (
    find_version_in_file,
    update_version_in_file,
)


def git(*args):
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout.strip()


class GitRepoTestCase(unittest.TestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)
        git("init", "-q")
        git("config", "user.email", "test@example.com")
        git("config", "user.name", "Test")
        git("config", "commit.gpgsign", "false")
        git("config", "tag.gpgsign", "false")
        os.environ.pop("GITHUB_OUTPUT", None)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.tmp.cleanup()

    def write(self, path, content):
        with open(path, "w") as f:
            f.write(content)

    def read(self, path):
        with open(path) as f:
            return f.read()

    def commit_all(self, msg="change"):
        git("add", ".")
        git("commit", "-qm", msg)

    def run_main(self, *argv):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(argv))
        return code, out.getvalue() + err.getvalue()


class TestMain(GitRepoTestCase):
    def test_bumps_all_files_with_single_tag_and_changelog(self):
        self.write("a.toml", 'version = "1.0.0"\n')
        self.write("b.json", '{"version": "1.0.0"}\n')
        self.commit_all("init")

        code, _ = self.run_main("a.toml", "b.json", "--minor", "--commit")

        self.assertEqual(code, 0)
        self.assertEqual(self.read("a.toml"), 'version = "1.1.0"\n')
        self.assertEqual(self.read("b.json"), '{"version": "1.1.0"}\n')
        self.assertEqual(git("tag"), "1.1.0")
        changelog = self.read("CHANGELOG.md")
        self.assertEqual(changelog.count("## "), 1)
        self.assertIn("[ minor ]", changelog)
        # the tag points at the bump commit, which contains all changes
        self.assertEqual(git("rev-list", "-n1", "1.1.0"), git("rev-parse", "HEAD"))
        self.assertEqual(git("status", "--porcelain"), "")

    def test_no_new_commits_does_not_bump(self):
        self.write("a.toml", 'version = "1.0.0"\n')
        self.commit_all("init")
        self.assertEqual(self.run_main("a.toml", "--commit")[0], 0)

        code, output = self.run_main("a.toml", "--commit")

        self.assertEqual(code, 0)
        self.assertIn("No updates", output)
        self.assertEqual(self.read("a.toml"), 'version = "1.0.1"\n')

        code, _ = self.run_main("a.toml", "--commit", "--force")
        self.assertEqual(code, 0)
        self.assertEqual(self.read("a.toml"), 'version = "1.0.2"\n')

    def test_bump_commits_are_left_out_of_changelog(self):
        self.write("a.toml", 'version = "1.0.0"\n')
        self.commit_all("init")
        self.run_main("a.toml", "--commit")
        self.write("other.txt", "x")
        self.commit_all("real change")

        self.run_main("a.toml", "--commit")

        latest_entry = self.read("CHANGELOG.md").split("## ")[1]
        self.assertIn("real change", latest_entry)
        self.assertNotIn("[skip ci]", latest_entry)

    def test_without_commit_files_change_but_no_tag(self):
        self.write("a.toml", 'version = "1.0.0"\n')
        self.commit_all("init")

        code, _ = self.run_main("a.toml")

        self.assertEqual(code, 0)
        self.assertEqual(self.read("a.toml"), 'version = "1.0.1"\n')
        self.assertEqual(git("tag"), "")

    def test_dry_run_changes_nothing(self):
        self.write("a.toml", 'version = "1.0.0"\n')
        self.commit_all("init")

        code, output = self.run_main("a.toml", "--major", "--dry-run", "--commit")

        self.assertEqual(code, 0)
        self.assertIn("1.0.0 to 2.0.0", output)
        self.assertEqual(self.read("a.toml"), 'version = "1.0.0"\n')
        self.assertFalse(os.path.exists("CHANGELOG.md"))
        self.assertEqual(git("tag"), "")

    def test_mismatched_versions_change_nothing(self):
        self.write("a.toml", 'version = "1.0.0"\n')
        self.write("b.toml", 'version = "2.0.0"\n')
        self.commit_all("init")

        code, output = self.run_main("a.toml", "b.toml")

        self.assertEqual(code, 1)
        self.assertIn("different versions", output)
        self.assertEqual(self.read("a.toml"), 'version = "1.0.0"\n')

    def test_existing_tag_is_an_error(self):
        self.write("a.toml", 'version = "1.0.0"\n')
        self.commit_all("init")
        git("tag", "1.0.1")
        self.write("other.txt", "x")
        self.commit_all("change")

        code, output = self.run_main("a.toml", "--commit")

        self.assertEqual(code, 1)
        self.assertIn("already exists", output)
        self.assertEqual(self.read("a.toml"), 'version = "1.0.0"\n')

    def test_errors_return_exit_code_without_traceback(self):
        self.write("a.toml", "no version\n")
        self.commit_all("init")
        self.assertEqual(self.run_main("a.toml")[0], 1)
        self.assertEqual(self.run_main("missing.toml")[0], 1)
        self.assertEqual(self.run_main("--patch")[0], 1)
        self.assertEqual(self.run_main("a.toml", "--change_msg_file", "nope")[0], 1)

    def test_conflicting_bump_flags_are_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_main("a.toml", "--major", "--minor")

    def test_github_output(self):
        self.write("a.toml", 'version = "1.0.0"\n')
        self.commit_all("init")
        output_file = os.path.join(self.tmp.name, "gh_output")
        os.environ["GITHUB_OUTPUT"] = output_file
        try:
            self.run_main("a.toml", "--commit")
        finally:
            os.environ.pop("GITHUB_OUTPUT")

        output = self.read(output_file)
        self.assertIn("bumped=true", output)
        self.assertIn("new_version=1.0.1", output)


class TestConfig(GitRepoTestCase):
    def test_config_uses_change_log_file_and_dry_run(self):
        self.write("a.toml", 'version = "1.0.0"\n')
        self.write(
            "c.yml",
            "settings:\n  bump_type: minor\n  files: [a.toml]\n  change_log_file: HISTORY.md\n",
        )
        self.commit_all("init")

        self.assertEqual(self.run_main("--config", "c.yml", "--dry-run")[0], 0)
        self.assertEqual(self.read("a.toml"), 'version = "1.0.0"\n')

        self.assertEqual(self.run_main("--config", "c.yml", "--commit")[0], 0)
        self.assertEqual(self.read("a.toml"), 'version = "1.1.0"\n')
        self.assertTrue(os.path.exists("HISTORY.md"))
        self.assertFalse(os.path.exists("CHANGELOG.md"))

    def test_invalid_configs_return_error(self):
        self.write("a.toml", 'version = "1.0.0"\n')
        self.commit_all("init")
        configs = [
            "settings:\n  bump_type: major\n  files: [a.toml]\n",
            "settings:\n  bump_type: huge\n  files: [a.toml]\n",
            "settings:\n  bump_type: patch\n",
            "just a string\n",
            "settings: [unclosed\n",
        ]
        for config in configs:
            with self.subTest(config=config):
                self.write("c.yml", config)
                code, output = self.run_main("--config", "c.yml")
                self.assertEqual(code, 1)
                self.assertNotIn("Traceback", output)


class TestVersionPatterns(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "pyproject.toml")

    def tearDown(self):
        self.tmp.cleanup()

    def test_similar_keys_are_ignored(self):
        content = (
            '[tool.black]\ntarget-version = "3.9.0"\n'
            'python_version = "3.8.0"\n'
            '[project]\nversion = "1.2.3"\n'
        )
        with open(self.path, "w") as f:
            f.write(content)

        self.assertEqual(find_version_in_file(self.path), "1.2.3")
        self.assertTrue(update_version_in_file(self.path, "1.2.3", "1.2.4", False))
        with open(self.path) as f:
            self.assertEqual(f.read(), content.replace("1.2.3", "1.2.4"))

    def test_only_first_occurrence_is_replaced_and_formatting_is_kept(self):
        content = "version='1.2.3'\n[tool.other]\nversion = \"1.2.3\"\n"
        with open(self.path, "w") as f:
            f.write(content)

        self.assertTrue(update_version_in_file(self.path, "1.2.3", "1.2.4", False))
        with open(self.path) as f:
            self.assertEqual(
                f.read(), "version='1.2.4'\n[tool.other]\nversion = \"1.2.3\"\n"
            )

    def test_v_prefixed_version_is_found(self):
        with open(self.path, "w") as f:
            f.write('version = "v1.2.3"\n')
        self.assertEqual(find_version_in_file(self.path), "v1.2.3")


if __name__ == "__main__":
    unittest.main()
