'''Define the message type to be used inside the network'''
from collections import namedtuple

FIELDS = (
    'event_type event_tags event_source timestamp device_info '
    'application_info user_info environment context effects data'
)
Message = namedtuple('Message', FIELDS)
