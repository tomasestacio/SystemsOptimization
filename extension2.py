from main import *
from calendar import c
from PolServer import PS_array, no_srv
import os
import glob
import pandas as pd
import numpy as np
import math

def ET_ext2(et_tasks):
    
    # reassignement of the priorities of the ET tasks according to lowest duration, biggest priority
    # 1) check the lowest duration of the ET tasks in the test case
    # 2) divide that by the number of ET tasks in the test case
    # 3) assign priorities based on the space division 

    big_ct = 0

    for task in et_tasks:
        if(big_ct < task.duration):
            big_ct = task.duration

    chunksize = math.floor(big_ct/7)
    if(big_ct % 7 > 0):
        chunksize += 1

    for task in et_tasks:
        for i in range(0, 7):
            if(task.duration <= chunksize*(i+1)):
                task.priority = i
                break

    return et_tasks
