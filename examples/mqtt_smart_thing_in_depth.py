# needed to run a local version of the AI
from ai.ai import AI

# the Highcliff actions to be tested
from highcliff.exampleactions import MonitorBodyTemperature, AuthorizeRoomTemperatureChange, ChangeRoomTemperature

# get a reference to the ai and its network
highcliff = AI.instance()
highcliff.connect()

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
goals = {"is_room_temperature_comfortable": True}
print(f'Start the search for the goals: {goals}')
highcliff.set_goals(goals)
highcliff.run(life_span_in_iterations=3)
