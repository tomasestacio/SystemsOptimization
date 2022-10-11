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
def create_poll_src(no_srv:int,hyperperiod):
    
    import numpy as np

    # Get hyperperiod divisors
    divList = list(divisorGenerator(hyperperiod))

    PS_matrix = np.zeros([1,6])

    for i in range(0,no_srv):
        # Choose a random divisor
        divisor = divList[np.random.randint(0,len(divList))]
        # Create a period from a divisor and multiple by consindering times 
        # divisor can be multiplied into lcm
        # period = np.random.randint(1,hyperperiod/divisor)*divisor
        period = divisor
        budget = np.random.randint(0,period)
        PS_def = ["tPS{0}".format(i+1),budget,period,"TT",7,period]
        
        if i == 0:
            PS_matrix = PS_def
        else:
            PS_matrix = np.vstack((PS_matrix,PS_def))

    ## [name, duration(budget), period, type, priority, deadline]
    ## [tPS1, int             , int   , TT  , 7       , int     ]

    ## Period is between 2 and hyperperiod of TT schedule
    ## deadline = period
    ## budget can be between 1 and the period, if it is the period it will occupy the CPU the entire time

    return PS_matrix

#a = list(divisorGenerator(12000))

PS_array = create_poll_src(1,12000)

print(PS_array)