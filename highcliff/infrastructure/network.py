# needed to make local variables behave like centralized infrastructure
from highcliff.singleton import Singleton

# needed for message queuing and validation
from jsonschema import validate, ValidationError
import json
import csv

# needed to reference the json schema file from within the host application
import pkgutil

# MQTT Networks
from awsiot import mqtt_connection_builder
from uuid import uuid4

class InvalidMessageFormat(Exception):
    pass


class InvalidTopic(Exception):
    pass


class ConnectionIsNotEstablished(Exception):
    pass


class Network:
    def __init__(self):
        pass

    def the_world(self):
        # returns a dictionary that describes the current state of the world
        raise NotImplementedError

    def update_the_world(self, update):
        # adds the given update to the persistent store of the world state
        raise NotImplementedError

    def create_topic(self, topic):
        f = open("topics.csv", "a")
        f.write(str(","+topic))
        f.close()
        # raise NotImplementedError

    def create_topic_file(self):
        f = open("topics.csv", "x")
        f.close()

    def read_topics(self,path):
        with open(path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)
        # raise NotImplementedError

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


@Singleton
class MqttNetwork(Network):
    __the_world = {}

    # refer to the package schema file in the host
    __json_schema_file_path = 'schema.json'

    def __init__(self):
        self.mqtt_connection = None
        json_schema_string = pkgutil.get_data(__name__, self.__json_schema_file_path).decode("utf-8")
        self.__json_schema = json.loads(json_schema_string)

    def connect(self, endpoint="a15645u9kev0b1-ats.iot.eu-west-2.amazonaws.com",
                port=8883, cert="/home/ubuntu/certs/certificate.pem.crt",
                key="/home/ubuntu/certs/private.pem.key",
                client_id=None, world_topic='world'):
        self.world_topic = world_topic
        if not client_id:
            client_id = "MqttNetwork-" + str(uuid4())
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        self.mqtt_client = mqtt_connection_builder.mtls_from_path(
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
        connect_future = mqtt_connection.connect()
        connect_future.result()
        self.subscribe_world()

    def subscribe_world(self):
       self.mqtt_client.subscribe(
            topic=self.world_topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self.process_world_update,
        )

    def publish(self, data):
        self.__validate_connection()
        payload = json.dumps(data)
        topic = self.world_topic
        print(f'Publising in topic {topic}: {payload}')
        self.mqtt_client.publish(
            topic=topic,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    def process_world_update(self, topic, payload, **kwargs):
        decoded_payload = str(payload.decode("utf-8", "ignore"))
        data = json.loads(decoded_payload)
        updated_data = {data['type']: data['value']}
        self.__the_world.update(updated_data)

    def update_the_world(self, update):
        self.__the_world.update(update)


    def the_world(self):
        return self.__the_world

    def __del__(self):
        if self.mqtt_connection is not None:
            print("Disconnecting...")
            disconnect_future = self.mqtt_connection.disconnect()
            disconnect_future.result()
            print("Disconnected!")

    @classmethod
    def __on_connection_interrupted(cls, connection, error, **kwargs):
        print("Connection interrupted. error: {}".format(error))

    @classmethod
    def __on_connection_resumed(cls, connection, return_code, session_present, **kwargs):
        print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(self.__on_resubscribe_complete)

    @classmethod
    def __on_resubscribe_complete(cls, resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))
        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))

    def __validate_message(self, json_message):
        # validate the schema against the message and raise an error if invalid
        try:
            validate(json_message, self.__json_schema)
        except ValidationError:
            raise InvalidMessageFormat

    def __validate_connection(self):
        if self.mqtt_client is None:
            raise ConnectionIsNotEstablished("Connection haven't been established, use connect method to do so")