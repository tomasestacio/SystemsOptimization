from main import *
import numpy as np
"""
    Ti - computation time -> t_list[i].duration
    Di - deadline -> t_list[i].deadline
    Pi - period -> t_list[i].period
"""
def dbf(t, t_list):
    """
    """
    sum = 0
    for task in t_list:
        if(task.type == "ET"):
            continue
        sum += ((t + task.period - task.deadline)/task.period)*task.duration
    return sum

def pdc(t_list):
    """
    """
    p = []
    for task in t_list:
        p.append(task.period)
    hyperperiod = np.lcm.reduce(p)
    ns=0
    s=0
    for t in range(1,hyperperiod):
        sum = dbf(t, t_list)
        if(sum > t):
            ns+=1
        if(sum < t):
            s+=1
    print(f"EDF Schedulable: {s}\n")
    print(f"EDF not Schedulable: {ns}")
    return 0

testcases_path = "/Users/joaomena/Documents/test_cases"
pdc(tasks_parser( testcases_path))