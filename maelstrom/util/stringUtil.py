"""
This module contains utility functions for strings
"""

import functools



def formatPercent(percentage: float)->str:
    return f'{percentage * 100}%'

def entab(original)->str:
    nl = "\n" # not allowed to have '\' in f string
    tab = "\t"
    return f'{tab}{original.replace(nl, nl + tab)}'

"""
Returns the length of the longest string in the given array
"""
def lengthOfLongest(strs: list[str])->int:
    strs = map(lambda str: len(str), strs)
    return functools.reduce(lambda bestLenSoFar, currLen: max(bestLenSoFar, currLen), strs, 0)
