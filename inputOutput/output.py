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

import sys

DEBUG = False
CLS_BEFORE_DISPLAY = True

class OutputConsumer:
    def output(self, *args, **kwargs):
        raise NotImplementedError("OutputConsumer::print is an abstract method")

class TerminalLogger(OutputConsumer):
    def output(self, *args, **kwargs):
        print(*args, **kwargs)

"""
class FileLogger(OutputConsumer):
"""

class DevNull(OutputConsumer):
    def output(self, *args, **kwargs):
        pass


outputConsumers = [TerminalLogger()]
errorConsumers = [TerminalLogger()]
debugConsumers = [TerminalLogger()]

def output(*args, **kwargs):
    for consumer in outputConsumers:
        consumer.output(*args, **kwargs)

def error(*args, **kwargs):
    localArgs = [f'Error: {arg}' for arg in args]

    localKwargs = kwargs.copy()
    if not "file" in localKwargs:
        localKwargs["file"] = sys.stderr

    for consumer in errorConsumers:
        consumer.output(*localArgs, **localKwargs)

def debug(*args, **kwargs):
    if DEBUG:
        for consumer in debugConsumers:
            consumer.output(*[f'DEBUG: {arg}' for arg in args], **kwargs)
