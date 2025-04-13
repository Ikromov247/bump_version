# Version Bumper

A tool to bump version numbers in project files. It can be used locally or as a GitHub Action.

## Features

- Bump minor, or patch versions (semantic versioning)
- Automatically detects version patterns in files
- Option to use Git tags as version source
- Can be used as a GitHub Action or CLI tool

# Installation

For now, the tool is only available as a script or Github Actions tool (recommended).
I have plans to publish it on pip soon.

## Usage

### CLI Usage

If you want to bump the version number in `setup.py`, 

```bash
# Bump patch version (default)
python main.py setup.py # 1.2.3 -> 1.2.4

# Specific bump types
python main.py setup.py --major # 1.2.3 -> 2.0.0
python main.py setup.py --minor # 1.2.3 -> 1.3.0
python main.py setup.py --patch # 1.2.3 -> 1.2.4

# Use Git tag as version, e.g. v0.9-19-g7e2d
python main.py setup.py --git 

# Pass several files to update
python main.py setup.py README.md --patch
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
description: 'Bump the patch version in dummy.py' # description

settings:
  bump_type: patch
  files: # list of files to update
    - setup.py
    - README.md
```

In cli, pass as an argument:
```python main.py --config config.yml```

In Github Actions workflow file:
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

## Contributing

If you want to contribute, start from checking the `todo` file. 
To suggest more features, create an issue with the tag `enhancement`.

## License

MIT
