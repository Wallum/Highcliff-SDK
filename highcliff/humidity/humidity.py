from highcliff.actions.actions import AIaction


class MonitorHumidity(AIaction):
    effects = {"problem_with_humidity": False}
    preconditions = {}

    def behavior(self):
        # decide if medication is needed and update the world accordingly
        raise NotImplementedError

    def __adjustment_needed(self):
        # this should be called by custom behavior if it determines that adjustment is needed
        self.effects["problem_with_humidity"] = True


class AuthorizeHumidityAdjustment(AIaction):
    effects = {"humidity_adjustment_authorized": True}
    preconditions = {"problem_with_humidity": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __authorization_failed(self):
        # this should be by custom behavior if it fails to confirm that the proper maintenance was given
        self.effects["humidity_adjustment_authorized"] = False
        self.effects["problem_with_humidity"] = True


class AdjustAirflow(AIaction):
    effects = {"problem_with_humidity": False}
    preconditions = {"humidity_adjustment_authorized": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __adjustment_failed(self):
        # this should be called by custom behavior if it fails to complete the adjustment
        self.effects["problems_with_humidity"] = True
