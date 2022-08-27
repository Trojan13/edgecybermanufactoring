import time
import pandas as pd
from random import randint


for i in range(100):
    waitTime = randint(50,100) / 1000
    time.sleep(waitTime)
    print(waitTime)
