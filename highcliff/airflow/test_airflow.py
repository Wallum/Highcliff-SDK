import pprint
import unittest
from highcliff.airflow import MonitorAirflow, AuthorizeAirflowAdjustment, AdjustAirflow
from highcliff.ai import AI
from highcliff.actions import ActionStatus

global airflow_sensor_reading_counter
global user_authorization_counter


def fake_airflow_sensor_reading():
    global airflow_sensor_reading_counter

    # sensor reading counter cycles between 1 and 3
    airflow_sensor_reading_counter += 1
    if airflow_sensor_reading_counter > 3:
        airflow_sensor_reading_counter = 1

    # the read out cycles between okay and too high
    sensor_readout = {
        1: "okay",
        2: "okay",
        3: "too high"
    }

    return sensor_readout[airflow_sensor_reading_counter]


def fake_user_authorization_response():
    global user_authorization_counter

    # user authorization counter cycles between 1 and 2
    user_authorization_counter += 1
    if user_authorization_counter > 2:
        user_authorization_counter = 1

    # the user authentication response cycles between yes and no
    user_response = {
        1: "no",
        2: "yes"
    }

    return user_response[user_authorization_counter]


class TestAirflow(unittest.TestCase):
    def setUp(self):
        # get a reference to the ai and its network
        self.highcliff = AI.instance()
        self.network = self.highcliff.network()

    def tearDown(self):
        # reset the ai
        self.highcliff.reset()

    def test_end_to_end_scenario(self):
        # test that the ai can create a plan to execute multiple actions and reach a goal

        global airflow_sensor_reading_counter
        global user_authorization_counter

        airflow_sensor_reading_counter = 0
        user_authorization_counter = 0

        class TestAirflowMonitor(MonitorAirflow):
            def behavior(self):
                # no adjustment needed if the sensor says that the airflow is okay
                if fake_airflow_sensor_reading() == "okay":
                    self.no_adjustment_needed()

        TestAirflowMonitor(self.highcliff)

        class TestAuthorizeAirflowChange(AuthorizeAirflowAdjustment):
            def behavior(self):
                if fake_user_authorization_response() == "no":
                    self.authorization_failed()

        TestAuthorizeAirflowChange(self.highcliff)

        class TestChangeAirflow(AdjustAirflow):
            def behavior(self):
                pass

        TestChangeAirflow(self.highcliff)

        # define the test world state and goals
        goal = {"is_airflow_comfortable": True}
        self.network.update_the_world({})
        self.highcliff.set_goals(goal)

        # run a local version of Highcliff
        self.highcliff.act(life_span_in_iterations=8)

        # did the ai recognize obstacles
        self.assertEqual(ActionStatus.FAIL, self.highcliff.diary()[0]["action_status"])
        self.assertEqual(ActionStatus.FAIL, self.highcliff.diary()[1]["action_status"])
        self.assertEqual(ActionStatus.SUCCESS, self.highcliff.diary()[2]["action_status"])
        self.assertEqual(ActionStatus.FAIL, self.highcliff.diary()[3]["action_status"])
        self.assertEqual(ActionStatus.SUCCESS, self.highcliff.diary()[4]["action_status"])
        self.assertEqual(ActionStatus.SUCCESS, self.highcliff.diary()[5]["action_status"])
        self.assertEqual(ActionStatus.SUCCESS, self.highcliff.diary()[6]["action_status"])
        self.assertEqual(ActionStatus.SUCCESS, self.highcliff.diary()[7]["action_status"])

        # did the ai make progress
        self.assertEqual(3, len(self.highcliff.diary()[2]["my_plan"]))
        self.assertEqual(2, len(self.highcliff.diary()[4]["my_plan"]))
        self.assertEqual(1, len(self.highcliff.diary()[5]["my_plan"]))
        self.assertEqual(0, len(self.highcliff.diary()[6]["my_plan"]))

        # did the ai reach the goal
        self.assertEqual(True, self.highcliff.diary()[6]["the_world_state_after"]["is_airflow_comfortable"])

        # did the ai stop after reaching the goal
        self.assertEqual(0, len(self.highcliff.diary()[6]["my_plan"]))
        self.assertEqual(0, len(self.highcliff.diary()[7]["my_plan"]))


if __name__ == '__main__':
    unittest.main()
