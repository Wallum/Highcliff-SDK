from datetime import datetime
import json
import time

import boto3


class Thing():
    def __init__(self, region, endpoint, device_id, device_type, publish_delay=30,
                 world_topic='world'):
        self.mqtt_client = boto3.client('iot-data', region_name=region, endpoint_url=endpoint)
        self.device_id = device_id
        self.device_type = device_type
        self.publish_delay = publish_delay
        self.world_topic = world_topic

    def run(self):
        while True:
            self.publish_data()
            time.sleep(self.publish_delay)

    def publish_data(self):
        payload = json.dumps({
            'device_id': self.device_id,
            'type': self.device_type,
            'sample_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'value': self.get_data(),
        })
        print(f'Publising in topic {self.world_topic}: {payload}')
        self.mqtt_client.publish(
            topic=self.world_topic,
            qos=1,
            payload=payload,
        )

    def get_data(self):
        raise NotImplementedError
