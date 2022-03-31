'''Manage messages information'''
from .message import Message

class Info():
    def __init__(self, topic, message):
        if not isinstance(message, Message):
            raise TypeError('Expected object of type Message')
        self.topic = topic
        self.check_message(message)
        self.message = message

    def __str__(self):
        return str(self.get_summary)

    @classmethod
    def check_message(cls, message):
        if message.event_source is None:
            raise TypeError('event_source attribute cannot be None')
        if message.timestamp is None:
            raise TypeError('timestamp attribute cannot be None')
        if message.event_type is None:
            raise TypeError('event_type attribute cannot be None')
        if (message.effects is not None and not isinstance(message.effects, dict)):
            raise TypeError(
                'effects attribute can be None or a list, but it is {type(message.effects)}')

    @property
    def device(self):
        return self.message.event_source

    def get_summary(self):
        return {self.device: {
            'topic': self.topic,
            'time': self.message.timestamp,
            'event_type': self.message.event_type,
            'location': self.location,
            'effects': self.message.effects,
            'data': self.message.data,
        }}

    @property
    def effects(self):
        return self.message.effects

    @property
    def location(self):
        if self.message.event_tags and 'location' in self.message.event_tags:
            return self.message.event_tags['location']
        return None
