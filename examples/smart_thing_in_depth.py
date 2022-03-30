__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2020 appliedAIstudio"
__version__ = "0.1"

# needed to get room temperature readings
from temperature_sensor import TemperatureScale, get_body_temperature

# needed to run a local version of the AI
from highcliff.ai import AI

# the Highcliff actions we are going to implement
from highcliff.exampleactions import MonitorBodyTemperature, AuthorizeRoomTemperatureChange, ChangeRoomTemperature

# get a reference to the ai and its network
highcliff = AI.instance()
network = highcliff.network()


# execute a single action with a single goal

class TestBodyTemperatureMonitor(MonitorBodyTemperature):
    def behavior(self):
        print("monitoring body temperature")


TestBodyTemperatureMonitor(highcliff)


class TestAuthorizeRoomTemperatureChange(AuthorizeRoomTemperatureChange):
    def behavior(self):
        print("getting permission to change the room temperature")


TestAuthorizeRoomTemperatureChange(highcliff)


class TestChangeRoomTemperature(ChangeRoomTemperature):
    def behavior(self):
        print("changing the room temperature")


TestChangeRoomTemperature(highcliff)


# define the world state, set goals, and run the ai
network.update_the_world({})
highcliff.set_goals({"is_room_temperature_comfortable": True})
highcliff.run(life_span_in_iterations=3)
