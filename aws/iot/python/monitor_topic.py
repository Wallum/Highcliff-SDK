#!/usr/bin/env python3

import argparse
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import sys
import time
from uuid import uuid4
import csv
import difflib
import os.path

def parse_args():
    parser = argparse.ArgumentParser(description="Send and receive messages through and MQTT connection.")
    # CHANGE PER SUBSCRIPTION ENDPOINT FOUND IN IOT CORE > SETTINGS
    parser.add_argument(
        '--endpoint',
        default="a15645u9kev0b1-ats.iot.eu-west-2.amazonaws.com",
        help="Your AWS IoT custom endpoint, not including a port. " +
             "Ex: \"abcd123456wxyz-ats.iot.us-east-1.amazonaws.com\""
    )
    parser.add_argument(
        '--port', default=8883, type=int,
        help="Specify port. AWS IoT supports 443 and 8883."
    )
    parser.add_argument(
        '--cert', default='/home/ubuntu/certs/certificate.pem.crt',
        help="File path to your client certificate, in PEM format."
    )
    parser.add_argument(
        '--key', default='/home/ubuntu/certs/private.pem.key',
        help="File path to your private key, in PEM format."
    )
    parser.add_argument(
        '--root-ca', default='/home/ubuntu/certs/AmazonRootCA1.pem',
        help="File path to root certificate authority, in PEM format."
    )
    parser.add_argument(
        '--client-id', default="test-" + str(uuid4()),
        help="Client ID for MQTT connection: use 'device' found in /home/ubuntu/vars"
    )
    parser.add_argument(
        '--topic', default="#", help="Topic to subscribe to. Wildcards can be used.")
    parser.add_argument(
        '--verbosity', choices=[x.name for x in io.LogLevel],
        default=io.LogLevel.NoLogs.name, help='Logging level'
    )
    parser.add_argument(
        '--topicspath', choices=[x.name for x in io.LogLevel],
        default="../../../topics.csv", help='path to topics file'
    )
    return parser.parse_args()


# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))

def flex(path):
    file_exists = os.path.exists(path)
    if file_exists == True:
        print(f"topics file {path} already exists")
    elif file_exists == False:
        f = open(path, "w")
        f.write("topic,desc")
        f.close()
        print(f"creating topics file at {path}")

def read(path):
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)

def diff(list, topic):
    difflist = difflib.get_close_matches(topic,list,cutoff=0.4)
    print(f"did you mean one of these topics? {difflist}")
    print("if no suitable topic listed, use:")
    print("'--topic=create:path,topic,desc' to create one")
    print("NO SPACES MUST BE USED")

def chck(path,topic):
    with open(path, 'r') as file:
        reader = csv.reader(file)
        topiclist=[]
        for row in reader:
            topiclist.append(row[0])
        if topic in topiclist:
            print(f"{topic} found!")
        else:
            print(f"couldnt find topic {topic}")
            diff(topiclist,topic)
            sys.exit()

def main():
    args = parse_args()
    # Spin up resources
    io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=args.endpoint,
        port=args.port,
        cert_filepath=args.cert,
        pri_key_filepath=args.key,
        client_bootstrap=client_bootstrap,
        ca_filepath=args.root_ca,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=args.client_id,
        clean_session=False,
        keep_alive_secs=30)

    print("Connecting to {} with client ID '{}'...".format(
        args.endpoint, args.client_id))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    if args.topic == "#":
        print("Subscribing to all topics")
    else:
        flex(args.topicspath)
        if args.topic == "#list#":
            read(args.topicspath)
        else:
            chck(args.topicspath, args.topic)
            print("Subscribing to topic '{}'...".format(args.topic))

    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=args.topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))
    while True:
        time.sleep(1)

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")


if __name__ == '__main__':
    main()
