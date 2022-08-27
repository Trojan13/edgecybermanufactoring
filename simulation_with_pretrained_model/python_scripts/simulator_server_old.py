from glob import glob
import random
import time
import json
from paho.mqtt import client as mqtt_client

currentIndex = 0
currentDataType = 'no'
MESSAGE_COUNT = 4

data_middle_motion = open('../data_analysis/data_middle_motion.json')
data_much_motion = open('../data_analysis/data_much_motion.json')
data_no_motion = open('../data_analysis/data_no_motion.json')

data_no_motion = json.load(data_no_motion)
data_middle_motion = json.load(data_middle_motion)
data_much_motion = json.load(data_much_motion)

simulationData = dict()
simulationData["no"] = data_no_motion["messages"]
simulationData["middle"] = data_middle_motion["messages"]
simulationData["much"] = data_much_motion["messages"]

broker = '192.168.178.53'
port = 1883
CONTROL_TOPIC = "python-simulator/control"
SEND_TEST_DATA_TOPIC = "acceleration"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'test'
password = 'test'


def send_messages(client):
    global currentIndex
    for i in range(MESSAGE_COUNT):
        if (len(simulationData[currentDataType]) < currentIndex + i):
            currentIndex = 0
        else:
            publish(
                client, simulationData[currentDataType][currentIndex]["payload"])
            currentIndex += i


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, msg):
    result = client.publish(SEND_TEST_DATA_TOPIC, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` ")
    else:
        print(f"Failed to send message")


def message_loop(client):
    while True:
        send_messages(client)
        time.sleep(5)


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global currentDataType
        global currentIndex
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        currentDataType = msg.payload.decode()
        currentIndex = 0
    client.subscribe(CONTROL_TOPIC)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    client.loop_start()
    subscribe(client)
    message_loop(client)


if __name__ == '__main__':
    run()
