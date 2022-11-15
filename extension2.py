from main import *
from calendar import c
from PolServer import PS_array, no_srv
import os
import glob
import pandas as pd
import numpy as np
import math

task_list = tasks_parser("testcases_seperation_tested_modified/testcases_seperation_tested")

def ET_ext2(task_list):
    # reassignement of the priorities of the ET tasks according to the EDF method -> earliest deadline, biggest priority
    # 1) check the biggest deadline of the ET tasks in the test case
    # 2) divide that by the number of ET tasks in the test case
    # 3) assign priorities based on the space division 

    et_tasks = []
    D = []
    P = []

    for task in task_list:
        if(task.type == "ET"):
            et_tasks.append(task)
            D.append(task.deadline)
            P.append(task.priority)

    max_deadline = 0

    for task in et_tasks:
        if(max_deadline < task.deadline):
            max_deadline = task.deadline

    chunksize = math.floor(max_deadline/7)

    for task in et_tasks:
        for i in range(0, 7):
            if(task.deadline - (i+1)*chunksize < 0):
                task.priority = i
                break

ET_ext2(task_list)