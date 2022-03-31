import rpyc

# AI, GOAP
from goap.action import Action


class AIAction(Action):
    _object_name = None

    def __init__(self, object_name, ai):

        self._object_name = object_name
        self.effects = {"prop1": "value1", "prop2": "value2", "prop3": "value3"}

    def act(self):
        print("ran", self._object_name)

    def get_name(self):
        return self._object_name

    def _integrate(self, ai):
        # as part of integration, an action registers itself as a capability for highcliff
        ai.add_capability(self)


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
    ai = connection.root.get_complex_object_runner()
    print("got a reference to a remote complex object runner")

    # create the new actions
    obj1 = AIAction("obj1", ai)
    obj2 = AIAction("obj2", ai)

    # explicitly register the actions with the ai
    ai.add_capability(obj1)
    ai.add_capability(obj2)

    print("created 2 actions with the remote ai")

    ai.run_complex_objects()
    print("ran the remote complex object runner")


if __name__ == "__main__":
    start_client()
