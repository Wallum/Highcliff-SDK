from collections import namedtuple
import json
import random
import time

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

Message = namedtuple('Message', 'event_type event_tags event_source timestamp device_info application_info user_info environment context effects data')

class Thing():
    def __init__(self, device_id, location=None, world_topic='world', publish_delay=30):
        self.device_id = device_id
        self.location = location
        self.publish_delay = publish_delay
        self.world_topic = world_topic
        self.mqtt_client = None

    def connect(self, endpoint, cert_filepath, pri_key_filepath):
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        self.mqtt_client = mqtt_connection_builder.mtls_from_path(
            client_id=self.device_id,
            endpoint=endpoint,
            client_bootstrap=client_bootstrap,
            cert_filepath=cert_filepath,
            pri_key_filepath=pri_key_filepath,
            on_connection_interrupted=self.__on_connection_interrupted,
            on_connection_resumed=self.__on_connection_resumed,
            clean_session=False,
            keep_alive_secs=30,
        )
        print(f'Connecting to {endpoint} with client ID {self.device_id}')
        connect_future = self.mqtt_client.connect()
        # Future.result() waits until a result is available
        connect_future.result()
        print('Connected')

    # Callback when connection is accidentally lost.
    def __on_connection_interrupted(self, connection, error, **kwargs):
        print(f'Connection interrupted. error: {error}')


    # Callback when an interrupted connection is re-established.
    def __on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        print(f'Connection resumed. return_code: {return_code} session_present: {session_present}')
        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print('Session did not persist. Resubscribing to existing topics...')
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(self.__on_resubscribe_complete)

    def __on_resubscribe_complete(self, resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print(f'Resubscribe results: {resubscribe_results}')

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit(f'Server rejected resubscribe to topic: {topic}')

    def run(self):
        while True:
            self.publish_data()
            time.sleep(self.publish_delay)

    def publish_data(self):
        data = Message(
            event_type=self.get_event_type(),
            event_tags=self.get_event_tags(),
            event_source=self.device_id,
            timestamp=time.time(),
            device_info=self.get_device_info(),
            application_info=self.get_application_info(),
            user_info=self.get_user_info(),
            environment=self.get_environment(),
            context=self.get_context(),
            effects=self.get_effects(),
            data=self.get_data(),
        )
        self.publish(self.world_topic, data)

    def get_event_type(self):
        raise NotImplementedError

    def get_event_tags(self):
        if self.location is not None:
            return {'location': self.location}
        return None

    def get_device_info(self):
        return None

    def get_application_info(self):
        return None

    def get_user_info(self):
        return None

    def get_environment(self):
        return None

    def get_context(self):
        return None

    def get_effects(self):
        return None

    def get_data(self):
        raise NotImplementedError

    def publish(self, topic, data):
        payload = json.dumps(data._asdict())
        print(f'Publising in topic {self.world_topic}: {payload}')
        self.mqtt_client.publish(
            topic=topic,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )



class InteractiveThing(Thing):
    def connect(self, endpoint, cert_filepath, pri_key_filepath):
        super().connect(endpoint, cert_filepath, pri_key_filepath)
        self.subscribe_requests_topic()

    def subscribe_requests_topic(self):
        requests_topic = f'{self.device_id}_request'
        print(f'Subscribing to requests topic {requests_topic}')
        self.mqtt_client.subscribe(
            self.get_requests_topic(),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self.receive_request
        )

    def receive_request(self, topic, payload, **kwargs):
        message = self.process_payload(payload)
        print(f'Received request in topic {topic}:\n\t{message}')
        if self.allowed(message.event_source):
            self.process_request(topic, message)
            self.publish_accepted(message)
            self.publish_data()
        else:
            self.pusblish_rejected(message)

    def allowed(self, device_id):
        return True

    def get_requests_topic(self):
        return f'{self.device_id}_request'

    def get_response_topic(self):
        return f'{self.device_id}_response'

    def publish_accepted(self, message):
        self.publish_allowance(message.event_source, True)

    def publish_rejected(self, message):
        self.publish_allowance(message.event_source, False)

    def publish_allowance(self, request_device_id, allowed):
        tags = self.get_event_tags()
        tags['requester_device'] = request_device_id

        data = Message(
            event_type='allowance',
            event_tags=tags,
            event_source=self.device_id,
            timestamp=time.time(),
            device_info=self.get_device_info(),
            application_info=self.get_application_info(),
            user_info=self.get_user_info(),
            environment=self.get_environment(),
            context=self.get_context(),
            effects=self.get_effects(),
            data=allowed,
        )
        self.publish(self.get_response_topic(), data)

    def process_request(self, topic, payload):
        raise NotImplementedError

    @classmethod
    def process_payload(cls, payload):
        decoded_payload = str(payload.decode("utf-8", "ignore"))
        return Message(**json.loads(decoded_payload))


class Thermometer(Thing):
    @classmethod
    def get_data(cls):
        return round(random.uniform(35.5, 42.5), 1)

    @classmethod
    def get_event_type(cls):
        return 'temperature'


class Thermostat(InteractiveThing):
    def __init__(self, device_id, location, world_topic, publish_delay, init_temperature=20):
        super().__init__(device_id, location, world_topic, publish_delay)
        self.temperature = init_temperature

    def get_data(self):
        return self.temperature

    @classmethod
    def get_event_type(cls):
        return 'configured_temperature'

    def process_request(self, topic, message):
        self.temperature = int(message.data)
