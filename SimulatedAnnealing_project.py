import time
import numpy as np

class simullated_annealing_parameters:
    def __init__(self,temperature,solution,cost,cooling_factor):
        self.curr_temp=temperature
        self.cool=cooling_factor
        self.best_solution=solution
        self.best_cost=cost

def cost_function(TT_tasks_WCRT,ET_tasks_WCRT,ET_schedule):

    coeficient=100
    sum_TT=0

    for i in TT_tasks_WCRT:
        sum_TT=sum_TT+i
    
    sum_ET=0

    for i in ET_tasks_WCRT:
        sum_ET=sum_ET+i

    #if the schedule for ET tasks is not possible, it will have a really big importance in the cost function
    #for that reason there is a coeficient 
    cost=sum_TT+sum_ET*(1+ET_schedule*coeficient)

    return cost

def SimulatedAnnealing(TT_tasks_WCRT,ET_tasks_WCRT,ET_schedule,candidate_solution,parameters):
    # Candidate cost
    candidate_cost = cost_function(TT_tasks_WCRT,ET_tasks_WCRT,ET_schedule)

    # if the new solution is better then accept it as the current solution
    if candidate_cost < parameters.best_cost:
        parameters.best_cost = candidate_cost
        parameters.best_solution = candidate_solution
        # if the solution is worse there is a random but decreasing chance to accept it
    else:
        if np.random.rand() < np.exp(-(candidate_cost - parameters.best_cost)/parameters.curr_temp):
            parameters.best_cost = candidate_cost
            parameters.best_solution=candidate_solution

    # reduce the temperature (we are still going to discuss about this)
    parameters.curr_temp = parameters.cool*parameters.curr_temp

    # return the new random changes to have the next candidates
    # we are still going to discuss about the boundaries
    
    max_number_poll_servers=4
    number_poll_servers=np.random.randint(1,max_number_poll_servers,1)
    max_budget=300
    min_budget=50
    budget_poll_servers=np.random.randint(min_budget,max_budget,size=1)
    min_period=100
    max_period=600
    period_poll_servers=np.random.randint(min_period,max_period,size=1)

    return number_poll_servers,budget_poll_servers,period_poll_servers


    