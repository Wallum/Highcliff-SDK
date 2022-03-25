'''Manage world status'''

from .info import Info

class World():
    def __init__(self):
        self.__information = {}
        self.__effects = {}

    def __str__(self):
        return str(self.get_all_info())

    def update(self, topic, message):
        try:
            info = Info(topic, message)
            self.__information[info.device] = info
            self.__effects.update(info.effects)
        except TypeError as err:
            print(f'Unable to proccess message from topic {topic}: {message}')
            raise

    def get_all_info(self):
        world = {}
        for _, info in self.__information.items():
            world.update(info.get_summary())
        return world

    @property
    def effects(self):
        return self.__effects
