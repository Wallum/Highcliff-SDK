__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

# needed to log events to the terminal window
import arrow


def log_event_to_the_terminal_window(event):
    time_stamp = arrow.utcnow().format('YYYY-MM-DD HH:mm:ss A')
    print(time_stamp, "|", event)
