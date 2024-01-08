"""
This script is used for managing Python project dependencies with Poetry.
It parses the pyproject.toml file, removes all dependencies except Python,
and then adds them back using the `poetry add` command. This is useful for
updating all dependencies to their latest versions.

This script also handles the removal of the poetry.lock file before updating
the dependencies.

This script accepts two optional command line arguments:
-p or --pyproject: Path to the pyproject.toml file (default is "pyproject.toml")
-l or --lockfile: Path to the poetry.lock file (default is "poetry.lock")
"""

import argparse
import os
import subprocess
from typing import Dict, List, Optional, Tuple

import toml
from loguru import logger

# Logger Configuration
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
)


def remove_poetry_lock(lock_file_path: str) -> None:
    """
    Remove the specified poetry lock file if it exists.

    Args:
        lock_file_path (str): Path to the poetry lock file.
    """
    # Check if the file exists
    if os.path.exists(lock_file_path):
        try:
            # Try to remove the file
            os.remove(lock_file_path)
            logger.info(f"Removed {lock_file_path}")
        except OSError as e:
            # Log an error if the file could not be removed
            logger.error(f"Error removing file {lock_file_path}: {e}")


def parse_and_update_toml(file_path: str) -> Dict[str, Dict]:
    """
    Parse the TOML file and extract package dependencies,
    updating the file by removing these dependencies except for Python.

    Args:
        file_path (str): Path to the TOML file.

    Returns:
        Dict[str, Dict]: Extracted package dependencies categorized by group.
    """
    try:
        # Open the file and load the TOML data
        with open(file_path, "r") as file:
            data = toml.load(file)

        packages = {}
        poetry_data = data.get("tool", {}).get("poetry", {})

        # Preserve Python dependency
        main_deps = poetry_data.get("dependencies", {})
        python_dep = main_deps.get("python", None)
        packages["main"] = {k: v for k, v in main_deps.items() if k != "python"}
        poetry_data["dependencies"] = {"python": python_dep} if python_dep else {}

        # Extract group dependencies and remove them from the TOML data
        for group, group_data in poetry_data.get("group", {}).items():
            group_deps = group_data.get("dependencies", {})
            packages[group] = group_deps
            group_data["dependencies"] = {}

        # Write the updated TOML data back to the file
        with open(file_path, "w") as file:
            toml.dump(data, file)

        return packages
    except Exception as e:
        logger.error(f"Error parsing and updating TOML file {file_path}: {e}")
        return {}


def generate_poetry_add_commands(packages: Dict[str, Dict]) -> List[str]:
    """
    Generate poetry add commands from the extracted packages.

    Args:
        packages (Dict[str, Dict]): Packages and their details.

    Returns:
        List[str]: List of poetry add commands.
    """
    commands = []
    for group, deps in packages.items():
        group_command_parts = []
        for pkg, details in deps.items():
            try:
                # Handle packages with extras
                if isinstance(details, dict) and "extras" in details:
                    extras = ",".join(details["extras"])
                    package_command = f"'{pkg}[{extras}]'@latest"
                else:
                    # Handle packages without extras
                    version = details if isinstance(details, str) else "latest"
                    package_command = f"{pkg}@latest"
                group_command_parts.append(package_command)
            except Exception as e:
                logger.error(f"Error generating command part for package {pkg}: {e}")

        # Generate the poetry add command for the group
        if group_command_parts:
            group_command = (
                "poetry add " + " ".join(group_command_parts) + f" --group {group}"
            )
            commands.append(group_command)

    return commands


def run_commands(commands: List[str]) -> None:
    """
    Execute the given list of commands.

    Args:
        commands (List[str]): List of commands to be executed.
    """
    for cmd in commands:
        try:
            # Log the command being executed
            logger.info(f"Executing: {cmd}")
            # Run the command
            subprocess.run(cmd, shell=True)
        except Exception as e:
            # Log an error if the command fails
            logger.error(f"Error executing command {cmd}: {e}")


def parse_arguments():
    """
    Parse command line arguments to get file paths for pyproject.toml and poetry.lock.

    Returns:
        argparse.Namespace: Parsed arguments with file paths.
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
    # Parse command line arguments
    args = parse_arguments()

    project_file_path = args.pyproject
    lock_file_path = args.lockfile

    # Remove the poetry lock file
    remove_poetry_lock(lock_file_path)

    try:
        # Parse the TOML file and update it
        packages = parse_and_update_toml(project_file_path)
        if packages:
            # Generate poetry add commands and run them
            commands = generate_poetry_add_commands(packages)
            run_commands(commands)
        else:
            logger.warning(
                "No packages found or an error occurred while parsing the TOML file."
            )
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
