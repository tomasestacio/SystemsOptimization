from main import * 
from math import gcd

testcases_path = 'C:\\Users\\Tiago Daily\\Desktop\\DTU\\SO\\test cases\\test cases'
def lcm(list):
    lcm = 1
    for i in list:
        lcm = lcm*i//gcd(lcm, i)
    return lcm


#ET_tasks is an array of tasks, each task has its own 
#characteristics (p,C,T,D)
#Cp Polling task budget/time 
#Tp Polling task period
#Dp Polling task Deadline
def ET_Schedule(ET_tasks,Cp,Tp,Dp):
    delta=Tp+Dp-2*Cp #in the future this is a parameter (extension 3) because this si the worst case possible and not the real one
    alfa=Cp/Tp
    #ET_tasks_size=len(ET_tasks)
    #T is the hyper period
    period_list=[]
    for task in ET_tasks:
        period_list.append(task.period)

    Hyperperiod =lcm(period_list)
    print(Hyperperiod)
    responseTime=[]
    for index ,actual_task in zip(range(len(ET_tasks)),ET_tasks):
        t=0   
        #t is the current time 
        responseTime.append(actual_task.deadline+1)
        #Initialize the response time of τi to a value exceeding the deadline
        #because if it's not schedulable, it is already done to return False

        while t<=Hyperperiod :
            supply=alfa*(t-delta)
            if(supply<0) :supply=0
            #linear supply bound function that will be important
            # to know the WCRT
            demand=0
            #now we need th subset of ET tasks that have higher priority
            # than the actual ET task
            demand_tasks=[]
            for task in ET_tasks:
                if (task.priority>=actual_task.priority): demand_tasks.append(task)
            
            #now we have everything to calculate the demand

            for task in demand_tasks:
                demand=demand+t*task.duration/task.period
            
            #after this the demand (Hi) is calculated and we jsut need to 
            #calculate if the supply and demand intersect, to know the 
            #responseTime
            #print(supply,demand)
            if supply>=demand and supply!=0: 
                responseTime[index]=t
                break
            #if supply >=demand , we found the response time and we can
            #go for the next task
            t=t+1
            #print(t)

        if responseTime[index]>actual_task.deadline:
            return False,responseTime

    return True,responseTime


task_list = tasks_parser(testcases_path)
ET_mask=[]
for task in task_list:
    ET_mask.append((task.type=='ET'))

ET_task_list= [ task for task, y in zip(task_list, ET_mask) if y == True]

#ET_task_list is th elist of ET tasks

print(ET_Schedule(ET_task_list[:8],300,500,2000))
