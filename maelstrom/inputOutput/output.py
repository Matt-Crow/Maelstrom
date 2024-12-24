"""
This file details which functions will receive program output and debug
information

Primary exports:
* output(*args, **kwargs)
* error(*args, **kwargs)
* debug(*args, **kwargs)

These functions forward their paramters to the official Python print function,
so anything that works for print will work for these
"""

from maelstrom.io import StandardOutputChannel
from maelstrom.util.config import get_global_config
import sys

standard_output = StandardOutputChannel()
outputConsumers = [standard_output]
errorConsumers = [standard_output]
debugConsumers = [standard_output]

def output(*args, **kwargs):
    for consumer in outputConsumers:
        consumer.write(*args, **kwargs)

def error(*args, **kwargs):
    localArgs = [f'Error: {arg}' for arg in args]

    localKwargs = kwargs.copy()
    if not "file" in localKwargs:
        localKwargs["file"] = sys.stderr

    for consumer in errorConsumers:
        consumer.write(*localArgs, **localKwargs)
    input("press any key to continue")

def debug(*args, **kwargs):
    if get_global_config().debug:
        for consumer in debugConsumers:
            consumer.write(*[f'DEBUG: {arg}' for arg in args], **kwargs)
