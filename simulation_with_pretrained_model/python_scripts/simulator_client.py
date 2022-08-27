import random
from paho.mqtt import client as mqtt_client
import numpy as np

broker = '192.168.178.53'
port = 1883
TOPIC = "edgevscloud"
CLIENT_TYPE = "EDGE"
client_id = f'{CLIENT_TYPE}-{random.randint(0, 1000)}'
username = 'test'
password = 'test'


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
    result = client.publish(TOPIC, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` ")
    else:
        print(f"Failed to send message")


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global testPingResults
        global testTaskResults
        decoded_msg = msg.payload.decode()
        if (msg.topic == TOPIC):
            split_msg = decoded_msg.split("_")
            if (split_msg[0] == "TASK"):
                client.publish(TOPIC, f'{CLIENT_TYPE}_TASK_{split_msg[1]}')
            elif (split_msg[0] == "PING"):
                print(f'{CLIENT_TYPE}_PONG_{split_msg[1]}')
                client.publish(TOPIC, f'{CLIENT_TYPE}_PONG_{split_msg[1]}')
    client.subscribe(TOPIC)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
