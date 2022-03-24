#!/usr/bin/env python3
import argparse
from datetime import datetime
import json
import time

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

from things import Message

class ConfigurationChanger():
    DEVICE_ID = 'configuration_changer'

    def __init__(self, device_to_change_id, world_topic):
        self.world_topic = world_topic
        self.device_to_change_id = device_to_change_id
        self.new_value = None

    def connect(self, endpoint, cert_filepath, pri_key_filepath):
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        self.mqtt_client = mqtt_connection_builder.mtls_from_path(
            client_id=self.DEVICE_ID,
            endpoint=endpoint,
            cert_filepath=cert_filepath,
            client_bootstrap=client_bootstrap,
            pri_key_filepath=pri_key_filepath,
            clean_session=True,
            keep_alive_secs=30)
        print(f'Connecting to {endpoint} with client ID {self.DEVICE_ID}')
        connect_future = self.mqtt_client.connect()
        # Future.result() waits until a result is available
        connect_future.result()
        print('Connected')

    def change_value(self):
        self.subscribe(self.world_topic, self.receive_world_state)
        self.subscribe(f'{self.device_to_change_id}_response', self.receive_response)
        time.sleep(60) # Wait to get state of the world

    def subscribe(self, topic, callback):
        print(f'Subscribing to topic {topic}')
        self.mqtt_client.subscribe(
            topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=callback,
        )

    def receive_world_state(self, topic, payload, **kwargs):
        decoded_payload = str(payload.decode("utf-8", "ignore"))
        data = json.loads(decoded_payload)
        message = Message(**data)
        print(f'Received message in topic {topic}:\n\t{message}')
        print(message.event_source)
        if message.event_source == self.device_to_change_id:
            if message.data != self.new_value:
                if self.new_value is None:
                    self.new_value = message.data + 4
                print(f'New value for the device: {self.new_value}')
                self.send_new_value()
            else:
                print(f'New value {self.new_value} already configured')

        else:
            print('Not interested in this device')

    def send_new_value(self):
        message = Message(
            event_type='allowance',
            event_tags={'requested_device': self.device_to_change_id},
            event_source=self.DEVICE_ID,
            timestamp=time.time(),
            device_info=None,
            application_info=None,
            user_info=None,
            environment=None,
            context=None,
            effects=None,
            data=self.new_value,
        )
        topic = f'{self.device_to_change_id}_request'
        print(f'Publising in topic {topic}: {message}')
        self.mqtt_client.publish(
            topic=topic,
            payload=json.dumps(message._asdict()),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    def receive_response(self, topic, payload, **kwargs):
        decoded_payload = str(payload.decode("utf-8", "ignore"))
        message = Message(**json.loads(decoded_payload))
        print(f'Received message in topic {topic}:\n\t{message}')
        if message.event_tags['requester_device'] != self.DEVICE_ID:
            print('Message not for me')
        else:
            print(f'Temperature change allowed: {message.data}')


def main(thermostat_device_id, topic, endpoint, cert_filepath, pri_key_filepath):
    configuration_changer = ConfigurationChanger(thermostat_device_id, topic)
    configuration_changer.connect(endpoint, cert_filepath, pri_key_filepath)
    configuration_changer.change_value()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate random temperatures and publish them.")
    parser.add_argument('--thermostat-device-id', default='thermostat-livingroom', type=str, help='Device id')
    parser.add_argument('--topic', default='world', type=str, help='MQtt topic.')
    parser.add_argument(
        '--endpoint',
        default="a15645u9kev0b1-ats.iot.eu-west-2.amazonaws.com",
        help="Your AWS IoT custom endpoint, not including a port. " +
             "Ex: \"abcd123456wxyz-ats.iot.us-east-1.amazonaws.com\""
    )
    parser.add_argument(
        '--cert_filepath', default='/home/ubuntu/certs/certificate.pem.crt',
        help="File path to your client certificate, in PEM format."
    )
    parser.add_argument(
        '--pri_key_filepath', default='/home/ubuntu/certs/private.pem.key',
        help="File path to your private key, in PEM format."
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    main(args.thermostat_device_id, args.topic, args.endpoint, args.cert_filepath, args.pri_key_filepath)
