#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

import argparse
from email.policy import default
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import sys
import threading
import time
from uuid import uuid4
import json
import csv
import difflib
import os.path

# This sample is based off the aws 'pubsub.py' example:
# https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/pubsub.py
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
        '--topic', default="test/temperatures",
        help="Topic to subscribe to, and publish messages to."
    )
    parser.add_argument(
        '--count', default=0, type=int,
        help="Number of messages to publish/receive before exiting."
    )
    parser.add_argument(
        '--data-file', default='temps.csv', type=str,
        help="File path for input data."
    )
    parser.add_argument(
        '--verbosity', choices=[x.name for x in io.LogLevel],
        default=io.LogLevel.NoLogs.name, help='Logging level'
    )
    return parser.parse_args()

args = parse_args()
io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')

received_count = 0
received_all_event = threading.Event()

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


# New function added to retrieve sample temp data from csv file:
# returns boolean value to reflect if there has been a temp change,
# along with temp value
def _checkTemp(file_name: str, historic_temp: float):
    f = open(file_name, "r")
    c = csv.reader(f, delimiter=',')

    for i, x in enumerate(c):
        if i == 0:
            new_temp = float(x[1])
            sample_time = x[0]
            if new_temp != historic_temp:
                return True, new_temp, sample_time
            else:
                return False, historic_temp, sample_time
    
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
    print("if no suitable topic listed, use ""-topic=create:path,topic,desc"" to create one")

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

def crte(path,topic,desc):
    f = open(path, "a+")
    f.write("\n"+topic+","+desc)
    f.close()
    print(f"creating topic {topic} in {path}")

# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    global received_count
    received_count += 1
    if received_count == args.count:
        received_all_event.set()

if __name__ == '__main__':
    # Spin up resources
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

    topic_default_path = "../../../topics.csv"
    flex(topic_default_path)

    if "create:" in args.topic:
        "create:path,topic,desc"
        paras1 = args.topic
        paras2 = paras1.split(":")[1]
        paras2.split(",")
        print(paras2[0]+","+paras2[1]+","+paras2[2])

    chck(topic_default_path, args.topic)

    # Subscribe
    print("Subscribing to topic '{}'...".format(args.topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=args.topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # Publish message to server desired number of times.
    # This step is skipped if message is blank.
    # This step loops forever if count was set to 0.
    if args.data_file:
        if args.count == 0:
            print ("Sending messages until program killed")
        else:
            print ("Sending {} message(s)".format(args.count))

        publish_count = 1
        historic_temp = 1
        while (publish_count <= args.count) or (args.count == 0):
            # obtain values using function
            is_temp_diff, current_temp, sample_time = _checkTemp(file_name=args.data_file, historic_temp=historic_temp)
            # publish a new mqtt message if there has been a temp change
            if is_temp_diff == True:
                j = {}
                j['device_id'] = args.client_id
                j['type'] = 'temperature'
                j['sample_time'] = sample_time
                j['value'] = current_temp
                message = json.dumps(j)
                print(f'Publishing in topic {args.topic}, message: {message}')
                mqtt_connection.publish(
                    topic=args.topic,
                    payload=message,
                    qos=mqtt.QoS.AT_LEAST_ONCE)
            historic_temp = current_temp
            time.sleep(1)
            publish_count += 1

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if args.count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
