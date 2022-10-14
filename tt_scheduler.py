# lcm for this case (inf10_10 first taskset) is equal to 12000
# for input, we have 30 TT tasks
from main import *
from calendar import c
from PolServer import PS_array
import os
import glob
import pandas as pd
import numpy as np

#choosing the task with earliest absolute deadline
def EDF(tt_tasks):
    trade = 9223372036854775807 #largest int number possible
    for task in tt_tasks:
        if(trade > task.deadline and task.duration != 0):
            trade = task.deadline
            EDFname = task.name 
    return EDFname

def edf_sim(task_list):

    tt_tasks = []
    C = []
    D = []
    p = []

    tt_tasks.append(PS_array)
    C.append(PS_array.duration)
    D.append(PS_array.deadline)
    p.append(PS_array.period)

    for task in task_list:
        if(task.type == "TT"):
            tt_tasks.append(task)
            C.append(task.duration)
            D.append(task.deadline)
            p.append(task.period)

    T = np.lcm.reduce(p)
    r = np.zeros(len(tt_tasks))
    wcrt = np.zeros(len(tt_tasks))
    sigma = []
    t = 0
    # We go through each slot in the schedule table until T 
    while t < T : 
        state = 0
        i = 0
        for task in tt_tasks:
            if(task.duration > 0 and task.deadline <= t): 
                print('Deadline miss!')
                
            if(task.duration == 0 and task.deadline >= t):
                if((t-r[i]) >= wcrt[i]): #Check if the current WCRT is larger than the current maximum.
                    wcrt[i] = t-r[i]
            if(t % task.period == 0):
                r[i] = t
                task.duration = C[i]
                task.deadline = t + D[i]

            i += 1
        
        for task in tt_tasks:
            if(task.duration != 0):
                #there are still tasks that have computation time, so lets break this loop and compute them, after checking EDF
                state = 1
                break

        if(state == 1):
            EDFname = EDF(tt_tasks)
            sigma.append(EDFname)
            for task in tt_tasks:
                if(EDFname == task.name):
                    task.duration -= 1 

        elif(state == 0):
            sigma.append("idle")

        t += 1

    for task in tt_tasks:
        if(task.duration > 0):
            print("Schedule is infeasible")

    print(sigma)
    print(wcrt)

    return sigma
