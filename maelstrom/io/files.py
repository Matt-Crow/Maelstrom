"""
File related utilities
"""

import json


def read_json_file(path: str) -> dict:
    """reads the given JSON file and returns its contents"""
    with open(path, mode='r') as file:
        contents = file.read()
    as_json = json.loads(contents)
    return as_json