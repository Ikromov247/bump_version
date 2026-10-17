# Version Bumper

A tool for developers to instantly bump version numbers in project files. It can be used locally or as a GitHub Action.

## Features

- Bump major, minor, or patch versions (semantic versioning)
- Commits the bump and tags the new commit (`--commit`)
- Creates and updates a changelog file with list of commits since the last git tag
- Can be used as a GitHub Action or from the command line

# Installation

Install the package using pip:
```bash
pip install simplebumpversion
```

## Usage

### CLI Usage

If you want to bump the version number in `setup.py`,

```bash
# Bump patch version (default)
bump-version setup.py # bumps 1.2.3 -> 1.2.4

# Specific bump types
bump-version setup.py --major # bumps 1.2.3 -> 2.0.0
bump-version setup.py --minor # bumps 1.2.3 -> 1.3.0
bump-version setup.py --patch # bumps 1.2.3 -> 1.2.4

# Pass several files to update (they must all contain the same version)
bump-version setup.py README.md --patch

# Commit the changed files and changelog, then tag the new commit
bump-version setup.py --patch --commit

# See what would change without changing anything
bump-version setup.py --patch --dry-run
```

Other options:

- `--changelog PATH`: changelog file to update (default `CHANGELOG.md`)
- `--change_msg TEXT` / `--change_msg_file PATH`: use this text for the changelog entry instead of the commits since the last tag
- `--force`: bump even if there are no new commits since the last tag

Without `--commit`, the files and changelog are changed but nothing is committed or tagged.
Automated `[skip ci]` commits, such as earlier bump commits, are left out of the changelog.

### GitHub Action Usage

```yaml
name: Bump Version

on:
  push:
    branches: [main]

# give permission to write and push commits
permissions:
  contents: write

jobs:
  bump-version:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required to find the last tag

      - name: Set git configurations
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"

      - name: Bump version
        id: bump
        uses: Ikromov247/bump_version@main
        with:
          files: 'package.json' # comma-separated files containing your package version number
          bump_type: 'patch'  # Options: major, minor, patch
          # commit: 'true'    # Optional: commit and tag the bump (default true)
          # force: 'false'    # Optional: bump even without new commits since the last tag
          # dry_run: 'false'  # Optional: only print what would change

      - name: Push changes
        if: steps.bump.outputs.bumped == 'true'
        run: git push --atomic origin HEAD:main "refs/tags/${{ steps.bump.outputs.new_version }}"
```

The action outputs `bumped` (`'true'` or `'false'`), `previous_version` and `new_version`.
If there are no new commits since the last tag, nothing is bumped and `bumped` is `'false'`.

### Config file

You can also add your configurations in a `yaml` file instead of passing them as arguments.
If you pass both the config file and the arguments, the files and bump type from the config file are used and those cli arguments are ignored.
Run options such as `--dry-run`, `--commit` and `--force` still apply.

Example configuration file:

```yaml
name: 'Patch bump' # Configuration name
description: 'Bump the patch version in setup.py and README.md' # description

settings:
  bump_type: patch
  files: # list of files to update
    - setup.py
    - README.md
  change_log_file: CHANGELOG.md # optional
```

In cli, pass the path to config file as an argument:
```bump-version --config config.yml```

Or use it in Github Actions workflow file:
```yaml
- name: Bump version
  uses: Ikromov247/bump_version@v2.1.0
  with:
    config: bump_config.yml
```


## Supported Version Formats

The tool recognizes uses regex to recognize various version patterns:

- `version = "1.2.3"`
- `VERSION = "1.2.3"`
- `__version__ = "1.2.3"`
- `"version": "1.2.3"` (for JSON/package.json)

## Common errors

- Invalid version format:
  - Reason: the tool could not find the version number. Your version possibly does not match supported patterns.

- File or permission errors:
  - Reason: the tool could not open or write to specified files.
  - Solution: check file paths and permissions.

- Config file is invalid:
  - Reason: your config file does not have required fields.
  - Solution: check the sample config file for reference.

- Major version bumping is not supported:
  - Reason: Bumping major versions is only possible through cli to prevent accidental major version bumps.
  - Solution: Use cli for major version bumps or set a different bump type

- Files contain different versions:
  - Reason: all files passed in one run must contain the same version.
  - Solution: make the versions match before bumping.

- Git tag already exists:
  - Reason: the new version was already tagged.
  - Solution: check the version in your files against your tags.

If your repo has no tags yet, all commits are treated as new.


## Contributing

If you want to contribute, start from checking the `todo` file and the CONTRIBUTING.MD for rules.
To suggest new features, create an issue with the tag `enhancement`.

## License

MIT
