import pandas as pd
import random
import time
from paho.mqtt import client as mqtt_client


broker = '192.168.178.53'
port = 1883
CONTROL_TOPIC = "control"
TOPIC = "edgevscloud"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'test'
password = 'test'

TEST_COUNT = 100
TEST_INTERVAL = 1
# [i] index tests [i][0] start [i][1] stop edge [i][2] stop cloud
testPingResults = [[0] * 3 for i in range(TEST_COUNT)]

# [i] index tests [i][0] start [i][1] stop edge [i][2] stop cloud
testTaskResults = [[0] * 3 for i in range(TEST_COUNT)]


def start_test_ping(client):
    global testPingResults
    for i in range(TEST_COUNT):
        time.sleep(TEST_INTERVAL)
        print(f"Send PING_`{i}`")
        client.publish(TOPIC, 'PING_'+str(i))
        testPingResults[i][0] = time.time()
    print(testPingResults)


def start_test_task(client):
    global testTaskResults
    for i in range(TEST_COUNT):
        print(f"Send TASK_`{i}`")
        client.publish(TOPIC, 'TASK_'+str(i))
        testTaskResults[i][0] = time.time()
        time.sleep(TEST_INTERVAL)
    print(testTaskResults)


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


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global testPingResults
        global testTaskResults
        decoded_msg = msg.payload.decode()
        if (msg.topic == CONTROL_TOPIC):
            print(f"Received control: `{decoded_msg}`")
        elif (msg.topic == TOPIC):
            split_msg = decoded_msg.split("_")
            print(f"Received stat: `{decoded_msg}`")
            if (split_msg[1] == "TASK"):
                if (split_msg[0] == "EDGE"):
                    testTaskResults[int(
                        split_msg[2])][1] = time.time()
                elif (split_msg[0] == "CLOUD"):
                    testTaskResults[int(
                        split_msg[2])][2] = time.time()
            elif (split_msg[1] == "PONG"):
                if (split_msg[0] == "EDGE"):
                    testPingResults[int(
                        split_msg[2])][1] = time.time()
                elif (split_msg[0] == "CLOUD"):
                    testPingResults[int(
                        split_msg[2])][2] = time.time()
    client.subscribe(CONTROL_TOPIC)
    client.subscribe(TOPIC)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()
    start_test_ping(client)
    time.sleep(10)
    start_test_task(client)
    global testPingResults
    global testTaskResults
    allDataArray = []
    for i in range(TEST_COUNT):
        taskTimeEdge = testTaskResults[i][2] - testTaskResults[i][0]
        taskTimeCloud = testTaskResults[i][1] - testTaskResults[i][0]
        pingTimeEdge = testPingResults[i][2] - testPingResults[i][0]
        pingTimeCloud = testPingResults[i][1] - testPingResults[i][0]
        allDataArray.append([pingTimeEdge, pingTimeCloud,
                            taskTimeEdge, taskTimeCloud])

    df = pd.DataFrame(allDataArray, columns=[
        'Ping Time Edge', 'Ping Time Cloud', 'Task Time Edge', 'Task Time Cloud'])
    df.to_csv('data.csv', index=False)


if __name__ == '__main__':
    run()
