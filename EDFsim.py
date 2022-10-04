# lcm for this case (inf10_10 first taskset) is equal to 12000
# for input, we have 30 TT tasks

import pandas as pd
import numpy as np

#choosing the task with earliest absolute deadline
def EDF(d, c):
    trade = 9223372036854775807 #largest int number possible
    for i in range(30):
        if(trade > d[i] and c[i] != 0):
            trade = d[i]
            index = i

    return index



filename = "test cases/test cases/inf_10_10/taskset__1643188013-a_0.1-b_0.1-n_30-m_20-d_unif-p_2000-q_4000-g_1000-t_5__99__tsk.csv"

data = pd.read_csv(filename, sep=';')
drop_rows = list(range(30, 50))
data.drop(drop_rows, axis=0, inplace=True)

datamatrix = data.values

name = datamatrix[:, 1]
duration = datamatrix[:, 2]
period = datamatrix[:, 3]
deadline = datamatrix[:, 6]

T = np.lcm.reduce(period)
print(T)
r = np.zeros(30)
sigma = []
used = np.zeros(1)
c = duration
d = deadline 
wcrt = np.zeros(30)
t = 0
# We go through each slot in the schedule table until T 
while t < T : 
    state = 0
    for i in range(30):
        if(c[i] > 0 and d[i] <= t): 
            print('Deadline miss!')
        if(c[i] == 0 and d[i] >= t):
            if((t-r[i]) >= wcrt[i]): #Check if the current WCRT is larger than the current maximum.
                wcrt[i] = (t-r[i])
        if(t % period[i] == 0):
            r[i] = t
            c[i] = duration[i]
            d[i] = t + deadline[i]
    
    for i in range(30):
        if(c[i] != 0):
            #there are still tasks that have computation time, so lets break this loop and compute them, after checking EDF
            state = 1
            break

    if(state == 1):
        ind = EDF(d, c)
        sigma.append(name[ind])
        c[ind] -= 1 

    elif(state == 0):
        sigma.append("TTidle")

    t += 1

for i in range(30):
    if(c[i] > 0):
        print("Schedule is infeasible")

#print(sigma)
#print(wcrt)
