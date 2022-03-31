__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

from highcliff.actions.actions import AIaction


class MonitorMedication(AIaction):
    effects = {"medication_needed": False}
    preconditions = {}

    def behavior(self):
        # decide if medication is needed and update the world accordingly
        raise NotImplementedError

    def __medication_needed(self):
        # this should be called by custom behavior if it determines that medication is needed
        self.effects["medication_needed"] = True
        self.effects["medication_requested"] = False


class RequestMedication(AIaction):
    effects = {"medication_requested": True}
    preconditions = {"medication_needed": True, "medication_requested": False}

    def behavior(self):
        # determine and request the needed medication
        raise NotImplementedError

    def __request_failed(self):
        # this should be called by custom behavior if it fails to complete the medication request
        self.effects["medication_requested"] = False


class ConfirmMedicationGiven(AIaction):
    effects = {"medication_needed": False}
    preconditions = {"medication_requested": True}

    def behavior(self):
        # get confirmation that the required medication was administered
        raise NotImplementedError

    def __confirmation_failed(self):
        # this should be by custom behavior if it fails to confirm that the proper medication was given
        self.effects["medication_needed"] = True
