"""
This module contains utility functions for strings
"""


def entab(original)->str:
    nl = "\n" # not allowed to have '\' in f string
    tab = "\t"
    return f'{tab}{original.replace(nl, nl + tab)}'
