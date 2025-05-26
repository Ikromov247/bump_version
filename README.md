# Version Bumper

A tool for developers to instantly bump version numbers in project files. It can be used locally or as a GitHub Action.

## Features

- Bump major, minor, or patch versions (semantic versioning)
- Option to use Git tags as version source
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

# Use Git tag as version, e.g. v0.9-19-g7e2d
bump-version setup.py --git

# Force the use of git tag when current version is semantic
bump-version setup.py --git --force

# Force conversion from git tag to semantic version
bump-version setup.py --patch --force

# Pass several files to update
bump-version setup.py README.md --patch
```

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
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Required for git versioning

      - name: Bump version
        uses: Ikromov247/bump_version@v0.9
        with:
          file: 'package.json' # file containing your package version number
          bump_type: 'patch'  # Options: major, minor, patch, git
          force: true    # Optional: Force version change when current version is a git tag

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "Bump version"
          git push

```

### Config file

You can also add your configurations in a `yaml` file instead of passing them as arguments.
If you pass both the config file and the arguments, config file takes precedence and cli arguments will be ignored.

Example configuration file:

```yaml
name: 'Patch bump' # Configuration name
description: 'Bump the patch version in setup.py and README.md' # description

settings:
  bump_type: patch
  files: # list of files to update
    - setup.py
    - README.md
  force: false # Set to true to force version change when current version is a git tag
```

In cli, pass the path to config file as an argument:
```bump-version --config config.yml```

Or use it in Github Actions workflow file:
```yaml
- name: Bump version
  uses: Ikromov247/bump_version@v0.9
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

- Current version is a git tag:
  - Reason: You're trying to bump a version that is currently a git tag.
  - Solution: Use the `--force` flag to convert it to a semantic version.

- Current version is semantic:
  - Reason: You're trying to replace a semantic version with a git tag.
  - Solution: Use `--git --force` to replace the semantic version with a git tag.

- File or permission errors:
  - Reason: the tool could not open or write to specified files.
  - Solution: check file paths and permissions.

- Config file is invalid:
  - Reason: your config file does not have required fields.
  - Solution: check the sample config file for reference.

- Major version bumping is not supported:
  - Reason: Bumping major versions is only possible through cli to prevent accidental major version bumps.
  - Solution: Use cli for major version bumps or set a different bump type

- Error occured when reading the git tag:
  - Reason: your repo does not have tags.
  - Solution: create a tag.


## Contributing

If you want to contribute, start from checking the `todo` file and the CONTRIBUTING.MD for rules.
To suggest new features, create an issue with the tag `enhancement`.

## License

MIT
