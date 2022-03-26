from highcliff.actions.actions import AIaction


class MonitorTemperature(AIaction):
    effects = {"problem_with_temperature": False}
    preconditions = {}

    def behavior(self):
        # decide if medication is needed and update the world accordingly
        raise NotImplementedError

    def _adjustment_needed(self):
        # this should be called by custom behavior if it determines that adjustment is needed
        self.effects["problem_with_temperature"] = True


class AuthorizeTemperatureAdjustment(AIaction):
    effects = {"temperature_adjustment_authorized": True}
    preconditions = {"problem_with_temperature": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def _authorization_failed(self):
        # this should be by custom behavior if it fails to confirm that the proper maintenance was given
        self.effects["temperature_adjustment_authorized"] = False
        self.effects["problem_with_temperature"] = True


class AdjustTemperature(AIaction):
    effects = {"problem_with_temperature": False}
    preconditions = {"temperature_adjustment_authorized": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def _adjustment_failed(self):
        # this should be called by custom behavior if it fails to complete the adjustment
        self.effects["problems_with_temperature"] = True
