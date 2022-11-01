import time
import numpy as np

class simullated_annealing_parameters:
    def __init__(self,temperature,solution,cost,cooling_factor,number_poll_servers,budget_poll_servers,period_poll_servers,norm_max):
        self.curr_temp=temperature
        self.cool=cooling_factor
        self.best_solution=solution
        self.best_cost=cost
        self.number_poll_servers=number_poll_servers
        self.budget_poll_servers=budget_poll_servers
        self.period_poll_servers=period_poll_servers
        self.iter=1
        self.norm_max=norm_max

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
        #Lower current temperature will decrease the chance of accepting worse solution
        candidate_cost_norm=np.interp(candidate_cost,[1,parameters.norm_max],[0,200])
        best_cost_norm=np.interp(parameters.best_cost,[1,parameters.norm_max],[0,200])
        if np.random.rand() < np.exp(-(candidate_cost_norm - best_cost_norm)/parameters.curr_temp):
            parameters.best_cost = candidate_cost
            parameters.best_solution=candidate_solution
    # reduce the temperature (we are still going to discuss about this)
    parameters.curr_temp = parameters.curr_temp/(1+parameters.cool*parameters.iter)

    parameters.iter+=1
    # return the new random changes to have the next candidates

    # we are still going to discuss about the boundaries
    
    max_number_poll_servers_variation=2
    number_poll_servers__variation=np.random.randint(-max_number_poll_servers_variation,max_number_poll_servers_variation,1)
    max_budget_variation=300
    budget_poll_servers_variation=np.random.randint(-max_budget_variation,max_budget_variation,size=1)
    max_period_variation=300
    period_poll_servers_variation=np.random.randint(max_period_variation,max_period_variation,size=1)

    #number_poll_servers=max(1,parameters.number_poll_servers+number_poll_servers__variation)
    budget_poll_servers=max(100,budget_poll_servers+budget_poll_servers_variation)
    #period_poll_servers=max(100,parameters.period_poll_servers+period_poll_servers_variation)

    period_poll_servers=100
    number_poll_servers=1
    parameters.number_poll_servers=number_poll_servers
    parameters.budget_poll_servers=budget_poll_servers
    parameters.period_poll_servers=period_poll_servers

    return number_poll_servers,budget_poll_servers,period_poll_servers


    