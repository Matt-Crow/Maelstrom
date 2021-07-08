"""
This file details which functions will receive program output and debug
information

Primary exports:
* output(msg)
* debug(msg)
"""

DEBUG = False

class OutputConsumer:
    def output(self, msg):
        raise NotImplementedError("OutputConsumer::print is an abstract method")

class TerminalLogger(OutputConsumer):
    def output(self, msg):
        print(msg);

"""
class FileLogger(OutputConsumer):
"""

class DevNull(OutputConsumer):
    def output(self, msg):
        pass


outputConsumers = [TerminalLogger()]
debugConsumers = [TerminalLogger()]

def output(msg):
    for consumer in outputConsumers:
        consumer.output(msg)

def debug(msg):
    if DEBUG:
        for consumer in debugConsumers:
            consumer.output(f'DEBUG: {msg}')
