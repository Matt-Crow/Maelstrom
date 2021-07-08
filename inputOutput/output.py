"""
This file details which functions will receive program output and debug
information

Primary exports:
* print(msg)
* debug(msg)
"""

DEBUG = False

class OutputConsumer:
    def print(self, msg):
        raise NotImplementedError("OutputConsumer::print is an abstract method")

class TerminalLogger(OutputConsumer):
    def print(self, msg):
        print(msg);

"""
class FileLogger(OutputConsumer):
"""

class DevNull(OutputConsumer):
    def print(self, msg):
        pass


outputConsumers = [TerminalLogger()]
debugConsumers = []
if DEBUG:
    debugConsumers.append(TerminalLogger())
else:
    debugConsumers.append(DevNull())

def print(msg):
    for consumer in outputConsumers:
        consumer.print(msg)

def debug(msg):
    for consumer in debugConsumers:
        consumer.print(msg)
