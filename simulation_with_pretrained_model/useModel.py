import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
import xgboost as xgb
import os


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
    xgb1.load_model("model.txt")

    y_pred = xgb1.predict(xgb.DMatrix(X_val))
    print(y_pred)


dir_path = './'
print("loading pressure files...")
pressureFile1 = get_files(dir_path=dir_path, filename='PS1.txt')
pressureFile2 = get_files(dir_path=dir_path, filename='PS2.txt')
pressureFile3 = get_files(dir_path=dir_path, filename='PS3.txt')
pressureFile4 = get_files(dir_path=dir_path, filename='PS4.txt')
pressureFile5 = get_files(dir_path=dir_path, filename='PS5.txt')
pressureFile6 = get_files(dir_path=dir_path, filename='PS6.txt')
print("loading flow files...")
volumeFlow1 = get_files(dir_path=dir_path, filename='FS1.txt')
volumeFlow2 = get_files(dir_path=dir_path, filename='FS2.txt')
print("loading temperature files...")
temperature1 = get_files(dir_path=dir_path, filename='TS1.txt')
temperature2 = get_files(dir_path=dir_path, filename='TS2.txt')
temperature3 = get_files(dir_path=dir_path, filename='TS3.txt')
temperature4 = get_files(dir_path=dir_path, filename='TS4.txt')
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
PS3 = pd.DataFrame(mean_conversion(pressureFile3))
PS3.columns = ['PS3']
PS4 = pd.DataFrame(mean_conversion(pressureFile4))
PS4.columns = ['PS4']
PS5 = pd.DataFrame(mean_conversion(pressureFile5))
PS5.columns = ['PS5']
PS6 = pd.DataFrame(mean_conversion(pressureFile6))
PS6.columns = ['PS6']
FS1 = pd.DataFrame(mean_conversion(volumeFlow1))
FS1.columns = ['FS1']
FS2 = pd.DataFrame(mean_conversion(volumeFlow2))
FS2.columns = ['FS2']
TS1 = pd.DataFrame(mean_conversion(temperature1))
TS1.columns = ['TS1']
TS2 = pd.DataFrame(mean_conversion(temperature2))
TS2.columns = ['TS2']
TS3 = pd.DataFrame(mean_conversion(temperature3))
TS3.columns = ['TS3']
TS4 = pd.DataFrame(mean_conversion(temperature4))
TS4.columns = ['TS4']
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

X = pd.concat([PS1, PS2, PS3, PS4, PS5, PS6, FS1, FS2, TS1,
              TS2, TS3, TS4, P1, VS1, CE1, CP1, SE1], axis=1)
X_normalize = StandardScaler().fit_transform(X)
y_pumpLeak = pd.DataFrame(profile.iloc[:, 2])


predict_pump_performance(X_normalize, y_pumpLeak, 'pump leaks')
