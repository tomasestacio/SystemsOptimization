import math
import functools as ft

#
def find_lcm(denominators):
    return ft.reduce(lambda a,b: a*b // math.gcd(a,b), denominators)

#
def divisorGenerator(n):
    large_divisors = []
    for i in range(1, int(math.sqrt(n) + 1)):
        if n % i == 0:
            yield i
            if i*i != n:
                large_divisors.append(int(n / i))
    for divisor in reversed(large_divisors):
        yield divisor

#
class Task:
    def __init__(self, task_dict):
        self.name = task_dict['name']
        self.duration = task_dict['duration']
        self.period = task_dict['period']
        self.type = task_dict['type']
        self.priority = task_dict['priority']
        self.deadline = task_dict['deadline']

#
def create_poll_src(no_srv:int,hyperperiod):
    
    import numpy as np

    # Get hyperperiod divisors
    divList = list(divisorGenerator(hyperperiod))

    PS_matrix = []

    for i in range(0,no_srv):
        # Choose a random divisor
        divisor = divList[np.random.randint(0,len(divList))]
        # Create a period from a divisor and multiple by considering times 
        # divisor can be multiplied into lcm
        # period = np.random.randint(1,hyperperiod/divisor)*divisor
        period = divisor
        budget = np.random.randint(0,period)
        PS_def_aux = {'name': "tPS{0}".format(i+1), 'duration': budget, 'period': period, 'type': "TT", 'priority': 7, 'deadline': period}
        print(PS_def_aux)
        PS_def = Task(PS_def_aux)

        PS_matrix.append(PS_def)

    ## [name, duration(budget), period, type, priority, deadline]
    ## [tPS1, int             , int   , TT  , 7       , int     ]

    ## Period is between 2 and hyperperiod of TT schedule
    ## deadline = period
    ## budget can be between 1 and the period, if it is the period it will occupy the CPU the entire time

    return PS_matrix

#a = list(divisorGenerator(12000))

# number of polling servers used (insert manually)
no_srv = 1

PS_array = create_poll_src(no_srv,12000)

print(PS_array)
