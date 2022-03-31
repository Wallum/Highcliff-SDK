__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

from highcliff.actions import AIaction


class MonitorBodyTemperature(AIaction):
    def __init__(self, ai):
        super().__init__(ai)
        self.effects = {"is_room_temperature_change_needed": True}
        self.preconditions = {}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError


class AuthorizeRoomTemperatureChange(AIaction):
    def __init__(self, ai):
        super().__init__(ai)
        self.effects = {"is_room_temperature_change_authorized": True}
        self.preconditions = {"is_room_temperature_change_needed": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError


class ChangeRoomTemperature(AIaction):
    def __init__(self, ai):
        super().__init__(ai)
        self.effects = {"is_room_temperature_comfortable": True}
        self.preconditions = {"is_room_temperature_change_authorized": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError
