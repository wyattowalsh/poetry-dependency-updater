# Python Project Dependency Updater

![Python Version](https://img.shields.io/badge/python-3.6-blue)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg)](https://www.gnu.org/licenses/gpl-3.0)

This script is designed to manage Python project dependencies using Poetry. It parses the `pyproject.toml` file, removes all dependencies except Python, and then adds them back using the `poetry add` command. This is useful for updating all dependencies to their latest versions.

The script also handles the removal of the `poetry.lock` file before updating the dependencies.

## Usage

The script accepts two optional command line arguments:

- `-p` or `--pyproject`: Path to the `pyproject.toml` file (default is "pyproject.toml")
- `-l` or `--lockfile`: Path to the `poetry.lock` file (default is "poetry.lock")

### Example

```shell
python updater.py --pyproject my_project/pyproject.toml --lockfile my_project/poetry.lock
```

## Requirements

The script requires Python 3.6 or higher and the following Python packages:

- `toml`
- `loguru`

These requirements can be installed using pip:

```bash
pip install -r requirements.txt
```

## License
This project is licensed under the terms of the [GNU General Public License v3.0](./LICENSE)
