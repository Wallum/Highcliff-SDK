__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

import os
import pprint
import unittest

from highcliff.exampleactions import MonitorBodyTemperature
from highcliff.ai import AI
from highcliff.actions import ActionStatus

# needed to start up the remote ai server
import rpyc
from ai_server import start_ai_server
from threading import Thread


class TestAI(unittest.TestCase):
    def setUp(self):
        # get a reference to the ai and its network
        self.highcliff = AI.instance()

    def tearDown(self):
        # reset the ai
        self.highcliff.reset()

    def test_shared_ai_reference(self):
        # create two instances of the ai
        first_ai = AI.instance()
        second_ai = AI.instance()

        # the two instances should be the same
        self.assertTrue(first_ai is second_ai)

        network_of_first_ai = first_ai.network()

        # the capabilities in AIs should initially be empty
        expected_capabilities = []
        self.assertEqual(expected_capabilities, first_ai.capabilities())
        self.assertEqual(expected_capabilities, second_ai.capabilities())

        # define a test body temperature monitor with a blank custom behavior
        class TestAction(MonitorBodyTemperature):
            def behavior(self):
                pass

        # instantiate the test body temperature monitor in the first ai
        test_action = TestAction(self.highcliff)

        # both the first and second ai should have the test action as a capability
        self.assertEqual(test_action, first_ai.capabilities()[0])
        self.assertEqual(test_action, second_ai.capabilities()[0])

        # define the test world state and goals
        network_of_first_ai.update_the_world({})
        first_ai.set_goals({"is_room_temperature_change_needed": True})

        # run a local version of Highcliff
        first_ai.run(life_span_in_iterations=1)

        # the ai diary should have content
        self.assertEqual(ActionStatus.SUCCESS, first_ai.diary()[0]['action_status'])

        # the two instances should still be the same after running one
        self.assertEqual(first_ai.diary(), second_ai.diary())

        # reset the ai
        first_ai.reset()

        # the capabilities of the ai should be gone
        self.assertEqual([], first_ai.capabilities())

        # the content of the ai diary should be gone
        self.assertEqual([], first_ai.diary())

        # the two instances should still be the same after resting one
        self.assertTrue(first_ai is second_ai)

    def test_goal_not_in_any_actions(self):
        # if the ai has no registered actions to achieve a goal, it should end with no plan

        # define a test body temperature monitor with a blank custom behavior
        class TestAction(MonitorBodyTemperature):
            def behavior(self):
                pass

        # instantiate the test body temperature monitor
        TestAction(self.highcliff)

        # define the test world state and goals
        network = self.highcliff.network()
        network.update_the_world({})
        self.highcliff.set_goals({"goal_not_in_the_test_action": True})

        # run a local version of Highcliff
        self.highcliff.run(life_span_in_iterations=1)

        # there should be no plan
        self.assertEqual(None, self.highcliff.diary()[0]['my_plan'])

    def test_goal_not_already_in_the_world(self):
        # if the ai encounters a goal not already in the world (in some state).
        # it should record that goal as unmet in the world

        # define a test body temperature monitor with a blank custom behavior
        class TestBodyTemperatureMonitor(MonitorBodyTemperature):
            def behavior(self):
                pass

        # instantiate the test body temperature monitor
        TestBodyTemperatureMonitor(self.highcliff)

        # define the network's world state and the AI's goals
        network = self.highcliff.network()
        network.update_the_world({})
        self.highcliff.set_goals({"is_room_temperature_change_needed": True})

        # run the ai
        self.highcliff.run(life_span_in_iterations=1)

        # before starting the first action, the ai should have notified the world that the goal was unmet
        unmet_goal = {"is_room_temperature_change_needed": False}
        self.assertEqual(unmet_goal, self.highcliff.diary()[0]['the_world_state_before'])

    def test_aimless_iterations(self):
        # the ai should be able to handle iterations with no goals

        # define an action (with a blank custom behavior)
        class TestAction(MonitorBodyTemperature):
            def behavior(self):
                pass

        # instantiate the action
        TestAction(self.highcliff)

        # define the network's world state and the AI's goals
        network = self.highcliff.network()
        network.update_the_world({})
        self.highcliff.set_goals({"is_room_temperature_change_needed": True})

        # run the ai
        self.highcliff.run(life_span_in_iterations=3)

        # it only takes 1 iteration for the ai to solve the problem
        # the remaining iterations should have no goal or plan
        no_goal = {}
        self.assertEqual(no_goal, self.highcliff.diary()[1]['my_goal'])
        self.assertEqual(no_goal, self.highcliff.diary()[2]['my_goal'])
        no_plan = []
        self.assertEqual(no_plan, self.highcliff.diary()[1]['my_plan'])
        self.assertEqual(no_plan, self.highcliff.diary()[2]['my_plan'])

    def test_run_and_connect_to_remote_ai_server(self):
        # run the remote server
        ai_server_thread = Thread(target=start_ai_server, daemon=True)
        ai_server_thread.start()

        # create a connection
        port = os.environ['port']
        connection = rpyc.connect("localhost", port)

        # verify the connection
        ai = connection.root.get_ai_instance()
        from highcliff.actions import AIaction

        # verify that we are connected to an object of the expected type
        expected_type_for_ai_object = "<netref class 'rpyc.core.netref.Singleton'>"
        self.assertEqual(expected_type_for_ai_object, str(type(ai)))


if __name__ == '__main__':
    unittest.main()
