__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2020 appliedAIstudio"
__version__ = "0.1"

# AI, GOAP
from goap.action import Action

# defines action status
from enum import Enum

# needed to copy the intended effects into the actual effects
import copy

# TODO: effects and preconditions should include topics specific to the action implementation


class AIaction(Action):

    def __init__(self, ai):

        # an action integrates itself with the communication infrastructure
        self._integrate(ai)

        # the intended effect of the action on the world
        self.effects = {}

        # the actual effect of the action on the world
        self.actual_effects = None

    def _integrate(self, ai):
        # as part of integration, an action registers itself as a capability for highcliff
        ai.add_capability(self)

    @staticmethod
    def update_the_world(network, update):
        # update the world state of highcliff
        network.update_the_world(update)

    def act(self, network):
        # assume that the act will have the intended effect
        self.actual_effects = copy.copy(self.effects)

        # every AI action runs custom behavior. this behavior may change the actual effects
        self.behavior()
        self.update_the_world(network, self.actual_effects)

    def behavior(self):
        # custom behavior must be specified by anyone implementing an AI action
        raise NotImplementedError


class ActionStatus(Enum):
    SUCCESS = 'success'
    FAIL = 'fail'

