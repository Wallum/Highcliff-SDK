__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2020 appliedAIstudio"
__version__ = "0.1"

# needed to run the ai
from highcliff.ai import AI

# needed to run the ai as a remote service
import rpyc

# needed to start the server in its own thread
from rpyc.utils.server import ThreadedServer

# needed to reference the json ai goal file
import json


class AIServer(rpyc.Service):
    def __init__(self, ai_goals_file):
        self._ai_instance = AI.instance()

        # get a reference to the centralized infrastructure
        network = self._ai_instance.network()

        # reset the world state
        network.update_the_world({})

        # determine the goals for the AI using the goals file
        with open(ai_goals_file) as json_file:
            ai_goals = json.load(json_file)
        self._ai_instance.set_goals(ai_goals)

        # set the AI to run indefinitely
        run_indefinitely = -1
        self._ai_instance.run(life_span_in_iterations=-run_indefinitely)

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_get_ai_instance(self):
        return self._ai_instance


def start_ai_server(ai_goals_file):
    # TODO: change the port to an environment variable
    thread = ThreadedServer(AIServer(ai_goals_file), port=18861)
    thread.start()


if __name__ == "__main__":
    start_ai_server("ai_goals.json")
