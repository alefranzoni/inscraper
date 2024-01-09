"""Module to handle all related to arguments."""
import argparse
from enum import Enum

class ArgumentOptions(Enum):
    """Enum class for command line argument options. Defines the available argument options."""
    ASK_LOGIN = "al"
    SCROLL_DELAY = "sd"
    SCROLL_RETRIES = "sr"
    GENERATE_KEY = "gk"

class ArgumentManager(object):
    """This class is responsible for managing command line arguments."""

    def __init__(self):
        """Initializes the instance by parsing command line arguments."""
        self.args = self._parse()

    def _parse(self):
        """Get the command line arguments passed by the user at runtime."""
        parser = argparse.ArgumentParser()
        group = parser.add_argument_group('login options')
        group.add_argument("-al", action="store_true", help="ask for login credentials from the user")
        group = parser.add_argument_group('scrolling options')
        group.add_argument("-sd", metavar="SCROLL_DELAY", type=float, help="add a delay (in seconds) to the scrolling process. Default is 0.5")
        group.add_argument("-sr", metavar="SCROLL_RETRIES", type=int, help="add attempts to the scrolling process. Default is 5")
        group = parser.add_argument_group("security options")
        group.add_argument("-gk", action="store_true", default=False, help="generate a new passkey to protect PII data")
        return parser.parse_args()

    def get(self, argument: ArgumentOptions):
        """Retrieves the value of a specific argument."""
        return getattr(self.args, argument.value)
