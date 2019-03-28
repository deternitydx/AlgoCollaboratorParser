import logging, sys

# Filters logs to be only contain or never contain the inputted level
class SingleLevelFilter(logging.Filter):
    def __init__(self, valid):
        self.valid_level = valid

    def filter(self, record):
        return (record.levelno in self.valid_level)