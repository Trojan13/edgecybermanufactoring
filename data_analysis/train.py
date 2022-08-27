import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf

print(f"TensorFlow version = {tf.__version__}\n")


# Set a fixed random seed value, for reproducibility, this will allow us to get
# the same random numbers each time the notebook is run
SEED = 1337
np.random.seed(SEED)
tf.random.set_seed(SEED)

# the list of MOVEMENTs that data is available for
MOVEMENTS = [
    "middle",
    "much",
    "no",
]

SAMPLES_PER_MOVEMENT = 5

NUM_MOVEMENTS = len(MOVEMENTS)

# create a one-hot encoded matrix that is used in the output
ONE_HOT_ENCODED_MOVEMENTS = np.eye(NUM_MOVEMENTS)

inputs = []
outputs = []

# read each csv file and push an input and output
for MOVEMENT_index in range(NUM_MOVEMENTS):
  MOVEMENT = MOVEMENTS[MOVEMENT_index]
  print(f"Processing index {MOVEMENT_index} for MOVEMENT '{MOVEMENT}'.")
  
  output = ONE_HOT_ENCODED_MOVEMENTS[MOVEMENT_index]
  
  df = pd.read_csv("data_" + MOVEMENT + "_motion.csv",sep=',')
  # calculate the number of MOVEMENT recordings in the file
  num_recordings = int(df.shape[0] / SAMPLES_PER_MOVEMENT)
  
  print(f"\tThere are {num_recordings} recordings of the {MOVEMENT} MOVEMENT.")
  
  for i in range(num_recordings):
    tensor = []
    for j in range(SAMPLES_PER_MOVEMENT):
      index = i * SAMPLES_PER_MOVEMENT + j
      # normalize the input data, between 0 to 1:
      # - acceleration is between: -4 to +4
      tensor += [
          (df['accel_x'][index] + 4) / 8,
          (df['accel_y'][index] + 4) / 8,
          (df['accel_z'][index] + 4) / 8,
      ]

    inputs.append(tensor)
    outputs.append(output)

# convert the list to numpy array
inputs = np.array(inputs)
outputs = np.array(outputs)

print("Data set parsing and preparation complete.")