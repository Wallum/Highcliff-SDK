__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

# needed to run a local version of the AI
from highcliff.ai import AI

# get a reference to the ai and its network
highcliff = AI.instance()
network = highcliff.network()

# create a topic
test_topic = "test_topic"
network.create_topic(test_topic)


# create a callback function to test publishing
def test_callback(topic, message):
    print("published this message: ", message)
    print("to this topic: ", topic)


# subscribe to the test topic
network.subscribe(test_topic, test_callback)

# publish a message to the subscribed topic
test_message = {
    "event_type": "publish_message",
    "event_tags": [],
    "event_source": "test_examples unit test",
    "timestamp": 1234567.89,
    "device_info": {},
    "application_info": {},
    "user_info": {},
    "environment": "test",
    "context": {},
    "effects": {},
    "data": {}
}

network.publish(test_topic, test_message)
