# needed to log events to the terminal window
import arrow


def log_event_to_the_terminal_window(event):
    time_stamp = arrow.utcnow().format('YYYY-MM-DD HH:mm:ss A')
    print(time_stamp, "|", event)
