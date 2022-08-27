import random
from paho.mqtt import client as mqtt_client
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
import xgboost as xgb
import os


broker = '192.168.178.53'
port = 1883
TOPIC = "edgevscloud"
CLIENT_TYPE = "CLOUD"
client_id = f'{CLIENT_TYPE}-{random.randint(0, 1000)}'
username = 'test'
password = 'test'


def setup_data():
    dir_path = '../'
    print("loading pressure files...")
    pressureFile1 = get_files(dir_path=dir_path, filename='PS1.txt')
    pressureFile2 = get_files(dir_path=dir_path, filename='PS2.txt')
    print("loading flow files...")
    volumeFlow1 = get_files(dir_path=dir_path, filename='FS1.txt')
    print("loading temperature files...")
    temperature1 = get_files(dir_path=dir_path, filename='TS1.txt')
    temperature2 = get_files(dir_path=dir_path, filename='TS2.txt')
    print("loading other files...")
    pump1 = get_files(dir_path=dir_path, filename='EPS1.txt')
    vibration1 = get_files(dir_path=dir_path, filename='VS1.txt')
    coolingE1 = get_files(dir_path=dir_path, filename='CE.txt')
    coolingP1 = get_files(dir_path=dir_path, filename='CP.txt')
    effFactor1 = get_files(dir_path=dir_path, filename='SE.txt')
    profile = get_files(dir_path=dir_path, filename='profile.txt')
    print("setting up data frames...")
    PS1 = pd.DataFrame(mean_conversion(pressureFile1))
    PS1.columns = ['PS1']
    PS2 = pd.DataFrame(mean_conversion(pressureFile2))
    PS2.columns = ['PS2']

    FS1 = pd.DataFrame(mean_conversion(volumeFlow1))
    FS1.columns = ['FS1']

    TS1 = pd.DataFrame(mean_conversion(temperature1))
    TS1.columns = ['TS1']
    TS2 = pd.DataFrame(mean_conversion(temperature2))
    TS2.columns = ['TS2']

    P1 = pd.DataFrame(mean_conversion(pump1))
    P1.columns = ['P1']
    VS1 = pd.DataFrame(mean_conversion(vibration1))
    VS1.columns = ['VS1']
    CE1 = pd.DataFrame(mean_conversion(coolingE1))
    CE1.columns = ['CE1']
    CP1 = pd.DataFrame(mean_conversion(coolingP1))
    CP1.columns = ['CP1']
    SE1 = pd.DataFrame(mean_conversion(effFactor1))
    SE1.columns = ['SE1']

    X = pd.concat([PS1, PS2, FS1, TS1,
                   TS2, P1, VS1, CE1, CP1, SE1], axis=1)
    X_normalize = StandardScaler().fit_transform(X)
    y_pumpLeak = pd.DataFrame(profile.iloc[:, 2])
    return [X_normalize, y_pumpLeak]


def mean_conversion(df):
    df1 = pd.DataFrame()
    df1 = df.mean(axis=1)
    return df1


def get_files(dir_path, filename):
    return pd.read_csv(os.path.join(dir_path, filename), sep='\t', header=None)


def predict_pump_performance(X, y, predictType):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=24)

    X_test, X_val, y_test, y_val = train_test_split(
        X_test, y_test, test_size=0.5, random_state=24)

    # we will use xgboost to do the classification
    xgb1 = xgb.Booster()
    xgb1.load_model("../model.txt")

    y_pred = xgb1.predict(xgb.DMatrix(X_val))


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


def subscribe(client: mqtt_client, normal, pump_leak):
    def on_message(client, userdata, msg):
        global testPingResults
        global testTaskResults
        decoded_msg = msg.payload.decode()
        if (msg.topic == TOPIC):
            split_msg = decoded_msg.split("_")
            if (split_msg[0] == "TASK"):
                predict_pump_performance(normal, pump_leak, 'pump leaks')
                client.publish(TOPIC, f'{CLIENT_TYPE}_TASK_{split_msg[1]}')
                print(f'{CLIENT_TYPE}_TASK_{split_msg[1]}')
            elif (split_msg[0] == "PING"):
                client.publish(TOPIC, f'{CLIENT_TYPE}_PONG_{split_msg[1]}')
                print(f'{CLIENT_TYPE}_PONG_{split_msg[1]}')
    client.subscribe(TOPIC)
    client.on_message = on_message


def run():
    normal, pump_leak = setup_data()
    client = connect_mqtt()
    subscribe(client, normal, pump_leak)
    client.loop_forever()


if __name__ == '__main__':
    run()
