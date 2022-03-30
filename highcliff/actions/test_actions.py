__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2020 appliedAIstudio"
__version__ = "0.1"

import unittest
from highcliff.actions import AIaction
from highcliff.ai import AI


class TestAction(AIaction):
    def __init__(self, ai):
        super().__init__(ai)
        self.effects = {"test_action_complete": True}
        self.preconditions = {}

    def behavior(self):
        # decide if adjustment is needed and update the world accordingly
        raise NotImplementedError

    def failure(self):
        # this should be called by custom behavior if it determines that no adjustment is needed
        self.actual_effects["test_action_complete"] = False


class SuccessfulAction(TestAction):
    def behavior(self):
        pass


class UnsuccessfulAction(TestAction):
    def behavior(self):
        self.failure()


class TestAIActions(unittest.TestCase):
    def setUp(self):
        # get a reference to the ai and its network
        self.highcliff = AI.instance()
        self.network = self.highcliff.network()

    def tearDown(self):
        # reset the ai
        self.highcliff.reset()

    def test_actual_effects_of_a_successful_act(self):
        # running an act successfully should have a predictable impact on the world
        test_successful_action = SuccessfulAction(self.highcliff)

        # the world should start empty
        self.assertEqual({}, self.network.the_world())

        # initiate the action
        test_successful_action.act(self.network)

        # the action should have the intended effect on the world
        self.assertEqual(test_successful_action.effects, self.network.the_world())

    def test_actual_effects_of_an_unsuccessful_act(self):
        # running an act successfully should have a predictable impact on the world
        test_unsuccessful_action = UnsuccessfulAction(self.highcliff)

        # the world should start empty
        self.assertEqual({}, self.network.the_world())

        # initiate the action
        test_unsuccessful_action.act(self.network)

        # the action should not have the intended effect on the world
        unintended_effect = {"test_action_complete": False}
        self.assertEqual(unintended_effect, self.network.the_world())

    def test_preconditions_and_effects_of_a_successful_action(self):
        # the preconditions and effects should be as expected before running the action
        test_successful_action = SuccessfulAction(self.highcliff)

        # the preconditions and effects of a successful act should be as expected before running
        self.assertEqual({}, test_successful_action.preconditions)
        self.assertEqual({"test_action_complete": True}, test_successful_action.effects)

        # initiate the action
        test_successful_action.act(self.network)

        # the preconditions and effects of a successful act should be as expected after running
        self.assertEqual({}, test_successful_action.preconditions)
        self.assertEqual({"test_action_complete": True}, test_successful_action.effects)

    def test_preconditions_and_effects_of_an_unsuccessful_action(self):
        # the preconditions and effects should be as expected before running the action
        test_unsuccessful_action = UnsuccessfulAction(self.highcliff)

        # the preconditions and effects of a successful act should be as expected before running
        self.assertEqual({}, test_unsuccessful_action.preconditions)
        self.assertEqual({"test_action_complete": True}, test_unsuccessful_action.effects)

        # initiate the action
        test_unsuccessful_action.act(self.network)

        # the preconditions and effects of a successful act should be as expected after running
        self.assertEqual({}, test_unsuccessful_action.preconditions)
        self.assertEqual({"test_action_complete": True}, test_unsuccessful_action.effects)


if __name__ == '__main__':
    unittest.main()
