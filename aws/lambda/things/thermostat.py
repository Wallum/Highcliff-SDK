import argparse

from things import Thing


class Thermostat(Thing):
    def __init__(self, region, endpoint, device_id, publish_delay, world_topic, init_temperature):
        super().__init__(region, endpoint, device_id, 'thermostat', publish_delay, world_topic)
        self.temperature = init_temperature

    def get_data(self):
        return self.temperature


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate random temperatures and publish them.")
    parser.add_argument('--topic', default='world', type=str, help='MQtt topic.')
    parser.add_argument('--publish-delay', default=30, type=int, help='Time between each published message')
    parser.add_argument('--endpoint', default='https://a15645u9kev0b1-ats.iot.eu-west-2.amazonaws.com', type=str, help='IOT MQtt endpoint.')
    parser.add_argument('--region', default='eu-west-2', type=str, help='AWS region')
    parser.add_argument('--device-id', default='thermostat-livingroom', type=str, help='Device id')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    thermostat = Thermostat(
        args.region,
        args.endpoint,
        args.device_id,
        args.publish_delay,
        args.topic,
        20,
    )
    thermostat.run()
