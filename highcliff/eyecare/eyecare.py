__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

from highcliff.actions.actions import AIaction


class MonitorEyes(AIaction):
    effects = {"problem_with_eyes": False}
    preconditions = {}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __eye_care_needed(self):
        # this should be called by custom behavior if it determines that care is needed
        self.effects["problem_with_eyes"] = True
        self.effects["eye_care_requested"] = False


class RequestEyeCare(AIaction):
    effects = {"problem_with_eyes": True, "eye_care_requested": True}
    preconditions = {"problem_with_eyes": True, "eye_care_requested": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __request_failed(self):
        # this should be called by custom behavior if it fails to complete the maintenance request
        self.effects["eye_care_requested"] = False


class ConfirmEyeCare(AIaction):
    effects = {"problem_with_eyes": False}
    preconditions = {"eye_care_requested": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __confirmation_failed(self):
        # this should be by custom behavior if it fails to confirm that the proper care was given
        self.effects["problem_with_eyes"] = True
