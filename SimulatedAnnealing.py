# SA for problem

# s = initial solutio

def TSP_SA(s):
    # SETUP
    import time
    import numpy as np
    # Initial cost
    c = some_cost_function(s)
    # Initial temperature
    T = 30
    # Cooling factor
    alpha = 0.99
    # Define simulation time
    tmax = 60 # [seconds]
    tstart = time.time()
    # SA solver
    while time.time() < tstart + tmax:
        # code to create some new solution that resuls in the following:
        c1 = "new cost"
        s1 = "new solution"

        # Compare those with the following
        # c  = initial cost
        # s  = initial solution
    
    # if the new solution is better then accept it as the current solution
    if c1 < c:
            s, c = s1, c1
    # if the solution is worse there is a random but decreasing chance to accept it
    else:
        if np.random.rand() < np.exp(-(c1 - c)/T):
            s, c = s1, c1
    # reduce the temperature
    T = alpha*T

    # return the accepted solution
    return s, c