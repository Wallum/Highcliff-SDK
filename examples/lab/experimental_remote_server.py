__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2020 appliedAIstudio"
__version__ = "0.1"

# needed to run the ai as a remote service
import rpyc

# needed to start the server in its own thread
from rpyc.utils.server import ThreadedServer


class AI:
    _capabilities = []

    def add_capability(self, action):
        self._capabilities.append(action)
        print("registered a complex object", action, "with effects", action.effects)

    def run_complex_objects(self):
        for complex_object in self._capabilities:
            print("running", complex_object.get_name(), "with effects", complex_object.effects)
            complex_object.act()
            print("ran a complex object")


class ExperimentalServer(rpyc.Service):
    _server_initialized = False
    _complex_object_runner = None

    def _init_server(self):
        self._complex_object_runner = AI()
        print("initialized server")

    def on_connect(self, conn):
        print("client connected")
        if not self._server_initialized:
            self._init_server()

        # initialization should not be repeated the next time a client connects
        self._server_initialized = True

    def on_disconnect(self, conn):
        pass

    def exposed_get_complex_object_runner(self):
        print("gave the client a reference to the complex object runner")
        return self._complex_object_runner


def start_server():
    thread = ThreadedServer(ExperimentalServer(),
                            port=12345,
                            protocol_config={"allow_all_attrs": True,
                                             "allow_public_attrs": True,
                                             "allow_setattr": True,
                                             "instantiate_custom_exceptions": True,
                                             "import_custom_exceptions": True
                                             }
                            )
    thread.start()
    print("started server")


if __name__ == "__main__":
    start_server()
