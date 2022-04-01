__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

# needed to make local variables behave like centralized infrastructure
from highcliff.singleton import Singleton

# needed for message queuing and validation
from jsonschema import validate, ValidationError
import json

# needed to reference the json schema file from within the host application
import pkgutil

# used to log system messages in the event of network connection failure
import sys

# MQTT Networks
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
from uuid import uuid4
import time

from .info import Info
from .message import Message
from .world import World


class InvalidMessageFormat(Exception):
    pass


class InvalidTopic(Exception):
    pass


class ConnectionIsNotEstablished(Exception):
    pass


class Network:

    def the_world(self):
        # returns a dictionary that describes the current state of the world
        raise NotImplementedError

    def update_the_world(self, update):
        # adds the given update to the persistent store of the world state
        raise NotImplementedError

    def create_topic(self, topic):
        # creates the given topic in the centralized message queue
        raise NotImplementedError

    def publish(self, topic, message):
        # uses the centralized message queue to publish the given message to the given topic
        raise NotImplementedError

    def subscribe(self, topic, callback_function):
        # registers the given callback function to be called by the centralized message queue
        # when a message is published to the given topic
        raise NotImplementedError


@Singleton
class LocalNetwork(Network):
    __the_world = {}
    __message_queue = {}

    # refer to the package schema file in the host
    __json_schema_file_path = 'schema.json'
    __json_schema_string = pkgutil.get_data(__name__, __json_schema_file_path).decode("utf-8")
    __json_schema = json.loads(__json_schema_string)

    def the_world(self):
        return self.__the_world

    def update_the_world(self, update):
        self.__the_world.update(update)

    def create_topic(self, topic):
        self.__message_queue[topic] = []

    def topics(self):
        return list(self.__message_queue.keys())

    def publish(self, topic, message):
        # raise an error to the caller if the topic is invalid
        try:
            self.__validate_topic(topic)
        except InvalidTopic:
            raise InvalidTopic

        self.__validate_message(message)

        # add the effects associated with the message to the world
        self.update_the_world(message["effects"])

        # call each callback function registered under the given topic
        for callback in self.__message_queue[topic]:
            callback(topic, message)

    def subscribe(self, topic, callback_function):
        # register the callback function under the given topic
        self.__message_queue[topic].append(callback_function)

    def reset(self):
        # clears all state
        self.__the_world = {}
        self.__message_queue = {}

    def __validate_topic(self, topic):
        # validate the the topic exists in the communication infrastructure
        if topic not in self.__message_queue.keys():
            raise InvalidTopic

    def __validate_message(self, json_message):
        # validate the schema against the message and raise an error if invalid
        try:
            validate(json_message, self.__json_schema)
        except ValidationError:
            raise InvalidMessageFormat


class MqttNetwork(Network):
    """Define and Network class that can be used by devices
    This class doesn't implement the world"""
    def __init__(self):
        """Init the MQTT client"""
        self.__mqtt_client = None

    def __del__(self):
        if self.__mqtt_client is not None:
            print("Disconnecting...")
            disconnect_future = self.__mqtt_client.disconnect()
            disconnect_future.result()
            print("Disconnected!")

    def connect(self, endpoint="a15645u9kev0b1-ats.iot.eu-west-2.amazonaws.com",
                port=8883, cert="/home/ubuntu/certs/certificate.pem.crt",
                key="/home/ubuntu/certs/private.pem.key", client_id=None):
        """Connect to an MQTT server"""
        if client_id is None:
            client_id = "HighCliff-" + str(uuid4())

        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        self.__mqtt_client = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            port=port,
            cert_filepath=cert,
            pri_key_filepath=key,
            client_bootstrap=client_bootstrap,
            on_connection_interrupted=self.__on_connection_interrupted,
            on_connection_resumed=self.__on_connection_resumed,
            client_id=client_id,
            clean_session=True,
            keep_alive_secs=30
        )
        connect_future = self.__mqtt_client.connect()
        connect_future.result()

    def publish(self, topic, message):
        """Publish a message in a topic"""
        self.__validate_connection()
        self.__validate_message(message)
        payload = json.dumps(message)
        print(f'Publishing in topic {topic}: {payload}')
        self.__mqtt_client.publish(
            topic=topic,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    def subscribe(self, topic, callback_function):
        """Subcribe to a topic"""
        self.__validate_connection()
        subscribe_future, _ = self.__mqtt_client.subscribe(
            topic=topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=callback_function,
        )
        subscribe_result = subscribe_future.result()
        print(f'Subscribed to {topic}')

    def create_topic(self, topic):
        """Doesn't need to create topics using
        awscrt.mqtt.Connection, they are created automatically"""
        pass

    def __validate_message(self, json_message):
        """Validate a message format"""
        try:
            validate(json_message, self.__json_schema)
        except ValidationError:
            raise InvalidMessageFormat

    def __validate_connection(self):
        """Validate that the connection has been established"""
        if self.__mqtt_client is None:
            raise ConnectionIsNotEstablished("Connection haven't been established, use connect method to do so")

    @classmethod
    def __on_connection_interrupted(cls, connection, error, **kwargs):
        """Execute on connection interrupted"""
        print("Connection interrupted. error: {}".format(error))

    @classmethod
    def __on_connection_resumed(cls, connection, return_code, session_present, **kwargs):
        """Execute on connection resume to restore everything"""
        print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(cls.__on_resubscribe_complete)

    @classmethod
    def __on_resubscribe_complete(cls, resubscribe_future):
        """Check resuscribe is completed"""
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))
        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))


@Singleton
class AiMqttNetwork(MqttNetwork):
    """MQTT Network that includes world implementation"""
    def __init__(self):
        super().__init__()
        self.__the_world = World()
        self.__world_topic = 'world'

    def connect(self, endpoint="a15645u9kev0b1-ats.iot.eu-west-2.amazonaws.com",
                port=8883, cert="/home/ubuntu/certs/certificate.pem.crt",
                key="/home/ubuntu/certs/private.pem.key", client_id=None):
        """Connect to an MQTT server and subscribe to every topic"""
        super().connect(endpoint, port, cert, key, client_id)
        self.__subscribe_everything()

    def __subscribe_everything(self):
        """Listen in every existing topic"""
        self.subscribe('#', self.process_external_world_update)

    def process_external_world_update(self, topic, payload, **kwargs):
        """Update the world for every message received"""
        decoded_payload = str(payload.decode("utf-8", "ignore"))
        data = json.loads(decoded_payload)
        print(f'Received from topic {topic} data: {data}')
        try:
            message = Message(**data)
            self.__the_world.update(topic, message)
        except TypeError as err:
            print(f'Error while processing message {data}: {err}')

    def update_the_world(self, update):
        """Update the world with given effects"""
        message = self.__create_message(update)
        self.publish(self.__world_topic, message._asdict())
        self.__the_world.update(self.__world_topic, message)

    @classmethod
    def __create_message(cls, effects):
        """Create a formated message given only the effects"""
        message = Message(
            event_type='effects',
            event_tags=None,
            event_source='highcliff_sdk',
            timestamp=time.time(),
            device_info=None,
            application_info=None,
            user_info=None,
            environment=None,
            context=None,
            effects=effects,
            data=None,
        )
        Info.check_message(message)
        return message

    def the_world(self):
        """Return the world effects"""
        return self.__the_world.effects
