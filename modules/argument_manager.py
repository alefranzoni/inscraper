import argparse
from enum import Enum

class ArgumentOptions(Enum):
    """
    Enum class for command line argument options. Defines the available argument options.
    """
    ASK_LOGIN = "ask_login"
    SCROLL_DELAY = "scroll_delay"
    SCROLL_RETRIES = "scroll_retries"

class ArgumentManager(object):
    """
    This class is responsible for managing command line arguments.
    """

    def __init__(self):
        """
        Initializes the instance by parsing command line arguments.
        """
        self.args = self._parse()

    def _parse(self):
        """
        Get the command line arguments passed by the user at runtime.
        """

        parser = argparse.ArgumentParser()

        group = parser.add_argument_group('login options')
        group.add_argument("-al", "--ask-login", action="store_true", help="ask for login credentials from the user")

        group = parser.add_argument_group('scrolling options')
        group.add_argument("-sd", "--scroll-delay", type=float, help="add a delay (in seconds) to the scrolling process. Default is 0.5")
        group.add_argument("-sr", "--scroll-retries", type=int, help="add attempts to the scrolling process. Default is 5")
        
        return parser.parse_args()

    def get(self, argument: ArgumentOptions):
        """
        Retrieves the value of a specific argument
        """

        return getattr(self.args, argument.value)
