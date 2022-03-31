__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

import unittest
from highcliff.logging import log_event_to_the_terminal_window

# needed to redirect terminal window output to a variable so that logging output can be tested
from io import StringIO
import sys


class MyTestCase(unittest.TestCase):
    def test_logging_event_to_terminal_window(self):
        # redirect terminal output to a variable and store the original terminal output
        # so that it can be restored at the end of the test
        text_captured_from_terminal = StringIO()
        terminal_window = sys.stdout
        sys.stdout = text_captured_from_terminal

        # test the logging function
        test_event = "test event"
        log_event_to_the_terminal_window(test_event)

        # check that the logging function wrote what was expected
        captured_text = text_captured_from_terminal.getvalue()
        self.assertTrue(test_event in captured_text)

        # restore the terminal output
        sys.stdout = terminal_window


if __name__ == '__main__':
    unittest.main()
