"""
Script to prepend a copyright header to all .py files in a directory tree.

Skips files inside __pycache__ directories and avoids adding duplicate headers.
"""

import datetime
import os
import re

current_year = datetime.datetime.now().year

# Header to be prepended to each Python file
HEADER = f'''"""
--------------------------------------------------------------------------
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © {current_year} Chris Rowles. All rights reserved.
License: MIT
--------------------------------------------------------------------------
"""
'''

HEADER_PATTERN = re.compile(
    r'^""".*?Author: Chris Rowles.*?License: MIT.*?"""(\r?\n)*',
    re.DOTALL
)


def should_skip(path: str) -> bool:
    """
    Determine whether a file should be skipped based on its path.

    Args:
        path (str): The full path to the file.

    Returns:
        bool: True if the file should be skipped, False otherwise.
    """
    return "__pycache__" in path or not path.endswith(".py")


def has_header(contents: str) -> bool:
    """
    Check if the file already contains the header.

    Args:
        contents (str): Contents of the file.

    Returns:
        bool: True if the header is already present, False otherwise.
    """
    return HEADER.strip() in contents


def prepend_header_to_file(filepath: str) -> None:
    """
    Add or replace the header at the top of a Python file.

    Args:
        filepath (str): The path to the file to modify.
    """
    with open(filepath, "r", encoding="utf-8") as file:
        contents = file.read()

    if HEADER_PATTERN.match(contents):
        # Replace the old header with the current HEADER
        new_contents = HEADER + "\n" + HEADER_PATTERN.sub('', contents, count=1).lstrip()
        action = "Docstring header replaced in"
    else:
        # Add HEADER at the top
        new_contents = HEADER + "\n" + contents
        action = "Docstring header added to"

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(new_contents)

    print(f"{action}: {filepath}")


def process_directory(root: str) -> None:
    """
    Recursively process all Python files in a directory tree.

    Args:
        root (str): The root directory to start from.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip __pycache__ directories
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if should_skip(full_path):
                continue
            prepend_header_to_file(full_path)


def insert_docstrings():
    """
    Insert docstrings into source files.
    """

    project_root = os.path.join(os.getcwd(), "src")
    process_directory(project_root)
