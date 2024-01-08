# Python Project Dependency Updater 🔄

![Python Version](https://img.shields.io/badge/python-3.6-blue)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg)](https://www.gnu.org/licenses/gpl-3.0)

> [!NOTE]
> This script manages Python project dependencies using Poetry. <br/>
> It ensures that your project dependencies are always up to date with the latest versions.

## 🚀 Features

- **Automated Dependency Updates**: Easily update all dependencies to their latest versions.
- **Lockfile Management**: Handles the removal and updating of the `poetry.lock` file.
- **Support for Command Line Arguments**: Customize the paths for your `pyproject.toml` and `poetry.lock` files.

## 📋 Usage

To use the script, you may provide two optional command line arguments:

- `-p` or `--pyproject`: Path to the `pyproject.toml` file (default: `"pyproject.toml"`)
- `-l` or `--lockfile`: Path to the `poetry.lock` file (default: `"poetry.lock"`)

### 🖥️ Command Line Example

```shell
python updater.py --pyproject my_project/pyproject.toml --lockfile my_project/poetry.lock
```

> [!TIP]
> Ensure you have the necessary permissions to modify the files in the specified directory.

## 🛠️ Requirements

> [!IMPORTANT]
> This script requires Python 3.6 or higher.

Dependencies:

- `toml`
- `loguru`

Install them using pip:

```bash
pip install -r requirements.txt
```

## ⚖️ License

> [!CAUTION]
> This project is licensed under the terms of the [GNU General Public License v3.0](./LICENSE). Make sure your use case complies with the license.
