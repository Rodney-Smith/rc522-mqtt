#!/usr/bin/python
import json
import os
import socket
import sys
import time

#import RPi.GPIO as gpio
#from mfrc522 import SimpleMFRC522
from pirc522 import RFID
import paho.mqtt.client as mqtt


def LOG(msg):
    print(msg)


def message(client, userdata, msg):
    # Method callled when a client's subscribed feed has a new value.
    LOG("Message received on topic {0}:{1}".format(msg.topic, str(msg.payload)))  # print a received msg
    #LOG("MQTT message received")
    pass


def connect(client, userdata, flags, rc):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    LOG("Flags: {0}\n RC: {1}".format(flags, rc)) # print result of connection attempt

    if rc == 0:
        LOG("Successfully connected to MQTT Broker!")
        client.publish(
            config['mqtt']['status_topic'], #topic
            "rc522 is up and running", #userdata
            qos=1,
            retain=True
        )
    else:
        LOG("Connection to MQTT Broker Failed!")
        sys.exit(1)


def disconnect(client, userdata, rc):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    LOG("Disconnected from MQTT Broker!")


def subscribe(client, userdata, topic, qos):
    # This method is called when the mqtt_client subscribes to a new feed.
    LOG("Subscribed to {0} with QOS level {1}".format(topic, qos))


def unsubscribe(client, userdata, topic, pid):
    # This method is called when the mqtt_client unsubscribes from a feed.
    LOG("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(client, userdata, topic):
    # This method is called when the mqtt_client publishes data to a feed.
    LOG("Published to {0}".format(topic))


def getConfig():
    # get configuration data from config.json file
    if os.path.isfile('./config.json'):
        with open('./config.json') as json_file:
            c = json.load(json_file)
    else:
        LOG("Could not find configuration file.")
        exit(1)
    # must have a mqtt broker
    if c['mqtt']['broker'] is None:
        LOG("Please supply an MQTT BROKER value.")
        exit(1)
    # must have a mqtt topic
    if c['mqtt']['topic'] is None:
        LOG("Please supply an MQTT TOPIC value.")
        exit(1)
    # must have a mqtt user
    if c['mqtt']['user'] is None:
        LOG("Please supply an MQTT USER value.")
        exit(1)
    # must have a mqtt password
    if c['mqtt']['password'] is None:
        LOG("Please supply an MQTT PASSWORD value.")
        exit(1)
    return c


def rfid_read(reader):
    uid_str = None
    LOG("Waiting for tag")
    reader.wait_for_tag()
    LOG("Found")
    (error, data) = reader.request()
    if not error:
        LOG("Detected: " + format(data, "02x"))
        (error, uid) = reader.anticoll()
        if not error:
            uid_str = ".".join(str(e) for e in uid)
            LOG("Card UID: " + uid_str)
        else:
            LOG("Error in anticoll")
    else:
        LOG("Error in request")

    return uid_str


def main():
    try:
        LOG("Attempting to connect to %s" % config['mqtt']['broker'])
        client.connect(host=config['mqtt']['broker'],port=config['mqtt']['port'])
    except socket.error as err:
        LOG(err)
        sys.exit(1)

    client.loop_start()

    reader = RFID()

    try:
        last_uid_str = None
        last_time = 0
        while True:
            uid_str = rfid_read(reader)
            td = time.time() - last_time
            if uid_str:
                if (uid_str != last_uid_str) or (td > 1):
                    last_uid_str = uid_str
                    client.publish(
                        config['mqtt']['event_topic'], #topic
                        uid_str, #userdata
                        qos=1,
                        retain=True
                    )
                time.sleep(0.1)
                last_time = time.time()
    except KeyboardInterrupt:
        LOG("KeyboardInterrupt")
    finally:
        reader.cleanup()
        client.publish(
            config['mqtt']['status_topic'], #topic
            "rc522 is not responding", #userdata
            qos=1,
            retain=True
        )
        client.disconnect()

    sys.exit(0)


# get the config
config = getConfig()
# create paho mqtt client object
client = mqtt.Client(
    client_id=config['mqtt']['clientid'],
    clean_session=True,
    userdata=None,
    transport="tcp"
)
client.username_pw_set(username=config['mqtt']['user'],password=config['mqtt']['password'])  # Create authentication
client.on_connect = connect  # define callback function for successful connection
client.on_disconnect = disconnect  # define callback function for successful disconnection
client.on_subscribe = subscribe  # define callback function for subscription to a topic
client.on_unsubscribe = unsubscribe  # define callback function for unsubscribing from a topic
#client.on_publish = publish  # define callback function for publishing of a message
client.on_message = message  # define callback function for receipt of a message

if __name__ == "__main__":
    main()

__author__ = "Rodney Smith"
__copyright__ = "Copyright 2022, RFID Card Reader Project"
__license__ = "MIT"
__version__ = "1.0.1"
__contact__ = "rodney.delauer@gmail.com"
__status__ = "Development"
