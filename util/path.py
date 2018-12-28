import os
import sys

"""
This modules is used to make it easier to add
directories to the path environment variable,
allowing you to use imports easier
"""

def add_subdir(subdir_name):
    """
    adds a subdirectory of the program to the path.
    if you are using Mac or Linux, appends
    "PROGRAM_DIRECTORY/subdir_name"
    to the path,
    if you are using Windows, appends
    "PROGRAM_DIRECTORY\\subdir_name to the path.
    """
    sys.path.append(os.path.join(os.getcwd(), subdir_name))