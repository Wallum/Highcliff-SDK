__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

from highcliff.actions.actions import AIaction


class MonitorLighting(AIaction):
    effects = {"problem_with_lighting": False}
    preconditions = {}

    def behavior(self):
        # decide if medication is needed and update the world accordingly
        raise NotImplementedError

    def __adjustment_needed(self):
        # this should be called by custom behavior if it determines that adjustment is needed
        self.effects["problem_with_lighting"] = True


class AuthorizeLightingAdjustment(AIaction):
    effects = {"lighting_adjustment_authorized": True}
    preconditions = {"problem_with_lighting": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __authorization_failed(self):
        # this should be by custom behavior if it fails to confirm that the proper maintenance was given
        self.effects["lighting_adjustment_authorized"] = False
        self.effects["problem_with_lighting"] = True


class AdjustLighting(AIaction):
    effects = {"problem_with_lighting": False}
    preconditions = {"lighting_adjustment_authorized": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __adjustment_failed(self):
        # this should be called by custom behavior if it fails to complete the adjustment
        self.effects["problems_with_lighting"] = True
