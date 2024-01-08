"""
This module, updater.py, is designed to automate the process of updating Python project dependencies 
using the Poetry dependency management tool. It offers functionality to handle updating dependencies 
to their latest versions, managing the 'poetry.lock' file, and supporting command line arguments to 
customize file paths.

The module is part of a project that requires Python 3.6 or higher and has dependencies on 'toml' and 'loguru' libraries.

Key Features:
- Automated Dependency Updates: Facilitates updating all project dependencies to their latest versions.
- Lockfile Management: Automates the removal and updating of the 'poetry.lock' file.
- Command Line Argument Support: Allows specifying custom paths for 'pyproject.toml' and 'poetry.lock' files.

Functions:
- setup_logging(): Configures the logging settings.
- remove_poetry_lock(lock_file_path): Removes the 'poetry.lock' file if it exists.
- parse_toml(file_path): Parses the TOML file and extracts package information.
- extract_packages(data): Extracts package information from parsed TOML data.
- update_toml(file_path, data): Updates the TOML file with new data.
- generate_poetry_add_commands(packages): Generates Poetry 'add' commands for the packages.
- generate_package_command(pkg, details): Generates a command part for a single package.
- run_command(command): Executes a shell command and logs its output.
- run_commands(commands): Runs a list of shell commands.
- parse_arguments(): Parses command-line arguments.

Usage:
This script can be executed from the command line, with optional arguments for specifying the paths to the 
'pyproject.toml' and 'poetry.lock' files. For example:
    python updater.py --pyproject my_project/pyproject.toml --lockfile my_project/poetry.lock

Dependencies:
- toml: A library for parsing and writing TOML files.
- loguru: A library for simplified logging.

Note:
This script is a part of a Python project licensed under the GNU General Public License v3.0. 
Ensure your use case complies with the license terms.
"""

import argparse
import os
import subprocess
from typing import Any, Dict, List, Tuple

import toml
from loguru import logger


def setup_logging():
    """
    Sets up logging configurations.
    """
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    )


def remove_poetry_lock(lock_file_path: str) -> None:
    """
    Removes the poetry lock file if it exists.

    Args:
        lock_file_path (str): Path to the poetry.lock file.
    """
    if os.path.exists(lock_file_path):
        try:
            os.remove(lock_file_path)
            logger.info(f"Removed {lock_file_path}")
        except OSError as e:
            logger.error(f"Error removing file {lock_file_path}: {e}")
            raise


def parse_toml(file_path: str) -> Tuple[Dict[str, Dict], Dict[str, Any]]:
    """
    Parses the TOML file and extracts package information.

    Args:
        file_path (str): Path to the TOML file.

    Returns:
        Tuple[Dict[str, Dict], Dict[str, Any]]: Extracted package information and updated data.
    """
    try:
        with open(file_path, "r") as file:
            data = toml.load(file)

        packages, updated_data = extract_packages(data)
        return packages, updated_data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error parsing TOML file {file_path}: {e}")
        raise


def extract_packages(data: Dict[str, Any]) -> Tuple[Dict[str, Dict], Dict[str, Any]]:
    """
    Extracts package information from the TOML data.

    Args:
        data (Dict[str, Any]): The parsed TOML data.

    Returns:
        Tuple[Dict[str, Dict], Dict[str, Any]]: Extracted package information and updated data.
    """
    packages = {}
    poetry_data = data.get("tool", {}).get("poetry", {})
    main_deps = poetry_data.get("dependencies", {})
    packages["main"] = {k: v for k, v in main_deps.items() if k != "python"}

    poetry_data["dependencies"] = {k: v for k, v in main_deps.items() if k == "python"}

    for group, group_data in poetry_data.get("group", {}).items():
        group_deps = group_data.get("dependencies", {})
        packages[group] = group_deps
        poetry_data["group"][group]["dependencies"] = {}

    return packages, data


def update_toml(file_path: str, data: Dict[str, Any]) -> None:
    """
    Updates the TOML file with new data.

    Args:
        file_path (str): Path to the TOML file.
        data (Dict[str, Any]): Data to write to the file.
    """
    try:
        with open(file_path, "w") as file:
            toml.dump(data, file)
            logger.info(f"Updated {file_path}")
    except Exception as e:
        logger.error(f"Error updating TOML file {file_path}: {e}")
        raise


def generate_poetry_add_commands(packages: Dict[str, Dict]) -> List[str]:
    """
    Generates poetry add commands for the packages.

    Args:
        packages (Dict[str, Dict]): The packages to generate commands for.

    Returns:
        List[str]: A list of poetry add commands.
    """
    commands = []
    for group, deps in packages.items():
        group_command_parts = []
        for pkg, details in deps.items():
            try:
                package_command = generate_package_command(pkg, details)
                group_command_parts.append(package_command)
            except Exception as e:
                logger.error(f"Error generating command for package {pkg}: {e}")

        if group_command_parts:
            command = "poetry add " + " ".join(group_command_parts)
            if group != "main":
                command += f" -G {group}"
            commands.append(command)

    return commands


def generate_package_command(pkg: str, details: Any) -> str:
    """
    Generates a command part for a single package.

    Args:
        pkg (str): The package name.
        details (Any): The package details.

    Returns:
        str: The generated command part.
    """
    if isinstance(details, dict) and "extras" in details:
        extras = ",".join(details["extras"])
        return f"'{pkg}[{extras}]'@latest"
    else:
        return f"{pkg}@latest"


def run_command(command: str) -> None:
    """
    Runs a shell command and logs its output.

    Args:
        command (str): The command to run.
    """
    try:
        logger.info(f"Executing: {command}")
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info(f"Output: {result.stdout.decode().strip()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command {command}: {e.stderr.decode().strip()}")
        raise RuntimeError(f"Command execution failed: {e}")


def run_commands(commands: List[str]) -> None:
    """
    Runs a list of shell commands.

    Args:
        commands (List[str]): The commands to run.
    """
    for cmd in commands:
        try:
            run_command(cmd)
        except RuntimeError as e:
            logger.error(f"Failed to execute command: {e}")
            break


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Poetry Dependency Management Script")
    parser.add_argument(
        "-p",
        "--pyproject",
        default="pyproject.toml",
        help="Path to the pyproject.toml file",
    )
    parser.add_argument(
        "-l", "--lockfile", default="poetry.lock", help="Path to the poetry.lock file"
    )
    return parser.parse_args()


if __name__ == "__main__":
    setup_logging()
    args = parse_arguments()

    try:
        packages, updated_data = parse_toml(args.pyproject)
        remove_poetry_lock(args.lockfile)
        update_toml(args.pyproject, updated_data)

        if packages:
            commands = generate_poetry_add_commands(packages)
            run_commands(commands)
        else:
            logger.warning("No packages found to update.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
