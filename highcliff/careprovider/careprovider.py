__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

from highcliff.actions.actions import AIaction


class AlertCareProvider(AIaction):
    effects = {"alert_care_provider": ...}
    preconditions = {}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError
