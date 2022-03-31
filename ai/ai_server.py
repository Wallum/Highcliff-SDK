__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

# needed to run the ai
import os

from ai import AI

# needed to run the ai as a remote service
import rpyc

# needed to start the server in its own thread
from rpyc.utils.server import ThreadedServer

# needed to reference the json ai goal file
import json

# needed to log initializing the server
from highcliff.logging import log_event_to_the_terminal_window

# needed to start ai server execution in its own thread
from threading import Thread


class AIServer(rpyc.Service):
    _ai_instance = AI.instance()
    _ai_initialized = False
    _debug_logging = os.environ["debug_logging"] == "True"

    def _init_ai(self):
        # log a debug event
        if self._debug_logging:
            log_event_to_the_terminal_window("Initializing the AI server")

        # set the debug logging level for the ai instance
        self._ai_instance.set_debug_logging(self._debug_logging)

        # get a reference to the centralized infrastructure
        network = self._ai_instance.network()

        # reset the world state
        network.update_the_world({})

        # log a debug event
        if self._debug_logging:
            log_event_to_the_terminal_window("The world state for the AI server has been reset")

        # determine the AI's goals using an external goals file
        with open("ai_goals.json") as json_file:
            ai_goals = json.load(json_file)
        self._ai_instance.set_goals(ai_goals)

        # log a debug event
        if self._debug_logging:
            log_event_to_the_terminal_window("The goals for the AI server have been set")

        # set the AI to run indefinitely and asynchronously in it's own thread of execution
        run_indefinitely = -1
        ai_execution_thread = Thread(target=self._ai_instance.run, kwargs={"life_span_in_iterations": run_indefinitely})
        ai_execution_thread.start()

        # log a debug event
        if self._debug_logging:
            log_event_to_the_terminal_window("AI Server is initialized")

    def on_connect(self, conn):
        if not self._ai_initialized:
            self._init_ai()

        # initialization should not be repeated the next time a client connects
        self._ai_initialized = True

    def on_disconnect(self, conn):
        pass

    def exposed_get_ai_instance(self):
        return self._ai_instance


def start_ai_server():
    port = int(os.environ["port"])
    thread = ThreadedServer(AIServer(), port=port, protocol_config={"allow_all_attrs": True,
                                                                    "allow_public_attrs": True,
                                                                    "allow_setattr": True,
                                                                    "instantiate_custom_exceptions": True,
                                                                    "import_custom_exceptions": True
                                                                    })
    thread.start()


if __name__ == "__main__":
    start_ai_server()
