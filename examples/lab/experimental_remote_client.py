import rpyc

# AI, GOAP
from goap.action import Action


class AIAction(Action):
    _object_name = None

    # ai that calls the action when needed
    _ai = None

    def __init__(self, object_name):
        self._object_name = object_name
        self.effects = {"prop1": "value1", "prop2": "value2", "prop3": "value3"}

    def act(self):
        print("ran", self._object_name)

    def get_name(self):
        return self._object_name


def start_client():
    print("starting client")

    # create a connection
    connection = rpyc.connect("localhost",
                              12345,
                              config={"allow_all_attrs": True,
                                      "allow_public_attrs": True,
                                      "allow_setattr": True,
                                      "instantiate_custom_exceptions": True,
                                      "import_custom_exceptions": True
                                      })
    print("connected to the experimental server")

    # get a reference to the complex object runner
    # verify the connection
    complex_object_runner = connection.root.get_complex_object_runner()
    print("got a reference to a remote complex object runner")

    obj1 = AIAction("obj1")
    obj2 = AIAction("obj2")
    complex_object_runner.register_complex_object(obj1)
    complex_object_runner.register_complex_object(obj2)
    print("registered 2 complex objects with the remote complex object runner")

    complex_object_runner.run_complex_objects()
    print("ran the remote complex object runner")


if __name__ == "__main__":
    start_client()
