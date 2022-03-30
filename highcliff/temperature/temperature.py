from highcliff.actions.actions import AIaction


class MonitorTemperature(AIaction):
    def __init__(self, ai):
        super().__init__(ai)
        self.effects = {"is_room_temperature_change_needed": True}
        self.preconditions = {}

    def behavior(self):
        # decide if medication is needed and update the world accordingly
        raise NotImplementedError

    def _no_adjustment_needed(self):
        # this should be called by custom behavior if it determines that no adjustment is needed
        self.actual_effects["is_room_temperature_change_needed"] = False


class AuthorizeTemperatureAdjustment(AIaction):
    def __init__(self, ai):
        super().__init__(ai)
        self.effects = {"is_room_temperature_change_authorized": True}
        self.preconditions = {"is_room_temperature_change_needed": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def _authorization_failed(self):
        # this should be by custom behavior if it fails to get authorization to make an adjustment
        self.actual_effects["is_room_temperature_change_authorized"] = False


class AdjustTemperature(AIaction):
    def __init__(self, ai):
        super().__init__(ai)
        self.effects = {"is_room_temperature_comfortable": True}
        self.preconditions = {"is_room_temperature_change_authorized": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def _adjustment_failed(self):
        # this should be called by custom behavior if it fails to complete the adjustment
        self.actual_effects["is_room_temperature_comfortable"] = False
