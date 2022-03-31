__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

from highcliff.actions.actions import AIaction


class MonitorCatheter(AIaction):
    effects = {"problem_with_catheter": False}
    preconditions = {}

    def behavior(self):
        # decide if medication is needed and update the world accordingly
        raise NotImplementedError

    def __maintenance_needed(self):
        # this should be called by custom behavior if it determines that maintenance is needed
        self.effects["problem_with_catheter"] = True
        self.effects["catheter_maintenance_requested"] = False


class RequestCatheterMaintenance(AIaction):
    effects = {"catheter_maintenance_requested": True}
    preconditions = {"problem_with_catheter": True, "catheter_maintenance_requested": False}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __request_failed(self):
        # this should be called by custom behavior if it fails to complete the maintenance request
        self.effects["catheter_maintenance_requested"] = False


class ConfirmCatheterMaintenance(AIaction):
    effects = {"problem_with_catheter": False}
    preconditions = {"catheter_maintenance_requested": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __confirmation_failed(self):
        # this should be by custom behavior if it fails to confirm that the proper maintenance was given
        self.effects["problem_with_catheter"] = True
