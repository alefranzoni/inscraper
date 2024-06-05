"""Module to handle all related to arguments."""
import argparse
from enum import Enum

class ArgumentOptions(Enum):
    """Enum class for command line argument options. Defines the available argument options."""
    SHOW_REPORT = "sr"
    GENERATE_KEY = "gk"

class ArgumentManager(object):
    """This class is responsible for managing command line arguments."""

    def __init__(self):
        """Initializes the instance by parsing command line arguments."""
        self.args = self._parse()

    def _parse(self):
        """Get the command line arguments passed by the user at runtime."""
        parser = argparse.ArgumentParser()
        parser.add_argument("-sr", metavar="USERNAME", type=str, help="show the last report generated for a given user")
        parser.add_argument("-gk", action="store_true", default=False, help="generate a new passkey to protect PII data")
        return parser.parse_args()

    def get(self, argument: ArgumentOptions):
        """Retrieves the value of a specific argument."""
        return getattr(self.args, argument.value)
