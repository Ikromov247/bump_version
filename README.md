# Version Bumper

A language-agnostic tool to bump version numbers in project files. It can be used locally or as a GitHub Action.

## Features

- Bump major, minor, or patch versions (semantic versioning)
- Automatically detects version patterns in files
- Option to use Git tags as version source
- Can be used as a GitHub Action or CLI tool

## CLI Usage

```bash
# Bump patch version (default)
python bump_version.py setup.py

# Specific bump types
python bump_version.py setup.py --major
python bump_version.py setup.py --minor
python bump_version.py setup.py --patch

# Use Git tag as version
python bump_version.py setup.py --git
```

## GitHub Action Usage

```yaml
name: Bump Version

on:
  push:
    branches: [main]

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

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "Bump version"
          git push

```

## Supported Version Formats

The tool recognizes various version patterns:

- `version = "1.2.3"`
- `VERSION = "1.2.3"`
- `__version__ = "1.2.3"`
- `"version": "1.2.3"` (for JSON/package.json)

## License

MIT
