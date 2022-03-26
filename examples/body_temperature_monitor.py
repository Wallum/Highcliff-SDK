__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2020 appliedAIstudio"
__version__ = "0.1"

# needed to get room temperature readings
from temperature_sensor import TemperatureScale, get_body_temperature

# the Highcliff actions we are going to implement
from highcliff.exampleactions import MonitorBodyTemperature

# needed to connect to the remote Highcliff AI
import rpyc


'''
The body temperature monitor application depends on a connection with the a remote ai server.
This code assumes that the ai server is up and running already.
'''


class BodyTemperatureMonitor(MonitorBodyTemperature):
    def behavior(self):
        print("monitoring body temperature")


def run_body_temperature_monitor():
    # create a connection. we assume that the ai server has been started at the specified ip address and port
    connection = rpyc.connect("localhost", 18861)
    highcliff_ai = connection.root.get_ai_instance()

    # run the body temperature model and register it with the highcliff ai
    BodyTemperatureMonitor(highcliff_ai)


if __name__ == "__main__":
    run_body_temperature_monitor()
