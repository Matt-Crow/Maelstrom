"""
Folder-related utilities
"""

from genericpath import isfile
from os import listdir
from os.path import join

def all_files_in(folder: str) -> 'list[str]':
    """gets a path to all files in the given folder - not recursive"""
    all_files_and_folders = [join(folder, f) for f in listdir(folder)]
    all_files = [f for f in all_files_and_folders if isfile(f)]
    return all_files