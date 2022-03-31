__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

from highcliff.actions.actions import AIaction


class MonitorBed(AIaction):
    effects = {"problem_with_bed": False}
    preconditions = {}

    def behavior(self):
        # decide if medication is needed and update the world accordingly
        raise NotImplementedError

    def __adjustment_needed(self):
        # this should be called by custom behavior if it determines that adjustment is needed
        self.effects["problem_with_bed"] = True


class AuthorizeBedAdjustment(AIaction):
    effects = {"bed_adjustment_authorized": True}
    preconditions = {"problem_with_bed": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __authorization_failed(self):
        # this should be by custom behavior if it fails to confirm that the proper adjustment was made
        self.effects["bed_adjustment_authorized"] = False
        self.effects["problem_with_bed"] = True


class AdjustBed(AIaction):
    effects = {"problem_with_bed": False}
    preconditions = {"bed_adjustment_authorized": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __adjustment_failed(self):
        # this should be called by custom behavior if it fails to complete the adjustment
        self.effects["problems_with_bed"] = True


class RequestBedAdjustment(AIaction):
    effects = {"bed_adjustment_requested": True}
    preconditions = {"problem_with_bed": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __request_failed(self):
        # this should be called by custom behavior if it fails to complete the adjustment request
        self.effects["bed_adjustment_requested"] = False


class ConfirmBedAdjustment(AIaction):
    effects = {"problem_with_bed": False}
    preconditions = {"bed_adjustment_requested": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __confirmation_failed(self):
        # this should be by custom behavior if it fails to confirm that the proper adjustment was made
        self.effects["problem_with_bed"] = True
