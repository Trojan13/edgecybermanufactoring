
import json
import random
from paho.mqtt import client as mqtt_client

broker = '192.168.178.53'
port = 1883
SEND_TEST_DATA_TOPIC = "acceleration"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
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


def send_stop(client):
    result = client.publish("actions/stop", "stop")
    status = result[0]
    if status == 0:
        print(f"Send stop")
    else:
        print(f"Failed to send message")


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        data = json.loads(msg.payload.decode())
        if "accel_z" in data:
            print(data['accel_z'])
            if abs(data["accel_z"]) > 5:
                print("Much")
                send_stop(client)
            elif abs(data["accel_z"]) > 2:
                print("Middle")
            elif abs(data["accel_z"]) > 2:
                print("No")

    client.subscribe(SEND_TEST_DATA_TOPIC)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
