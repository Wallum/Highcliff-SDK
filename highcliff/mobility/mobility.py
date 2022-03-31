__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

from highcliff.actions.actions import AIaction


class RequestMovement(AIaction):
    effects = {"movement_needed": True}
    preconditions = {}

    def behavior(self):
        # decide if medication is needed and update the world accordingly
        raise NotImplementedError

    def __request_failed(self):
        # this should be called by custom behavior if it determines that movement is not needed
        self.effects["movement_needed"] = False


class AuthorizeMovement(AIaction):
    effects = {"movement_authorized": True}
    preconditions = {"movement_needed": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __authorization_failed(self):
        # this should be by custom behavior if it fails to authorize the movement
        self.effects["movement_authorized"] = False
        self.effects["movement_needed"] = True


class Move(AIaction):
    effects = {"movement_needed": False}
    preconditions = {"movement_authorized": True}

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError

    def __movement_failed(self):
        # this should be called by custom behavior if it fails to complete the movement
        self.effects["movement_needed"] = True
