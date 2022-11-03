import time
import numpy as np

class simullated_annealing_parameters:
    def __init__(self, temperature, solution, cost,best_schedule, cooling_factor,norm_max):
        self.curr_temp=temperature
        self.cool=cooling_factor
        self.best_solution=solution
        self.best_cost=cost
        self.best_schedule=best_schedule
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
    cost=sum_TT/len(TT_tasks_WCRT)+sum_ET*(1+ET_schedule*coeficient)/len(ET_tasks_WCRT)

    return cost

def simulated_annealing(tt_tasks_wcrt, et_tasks_wcrt,tt_schedule, et_tasks_sched, candidate_solution, parameters, hyperperiod,tt_schedule_bool):
    """
    compares cost of proposed solution to the best solution and returns random values to test again
    :param tt_tasks_wcrt: time triggered tasks worst case response time
    :param et_tasks_wcrt: event triggered tasks worst case response time
    :param et_tasks_sched: event triggered tasks schedulability
    :param candidate_solution: list of parameters that make up the solution
    :param parameters: SimulatedAnnealingParams object
    :param hyperperiod: hyperperiod of all time triggered tasks including polling server
    :return: new number of polling servers, budget and period randomly generated
    """
    if(tt_schedule_bool==1):
        # calculate cost with the parameters given
        candidate_cost = cost_function(tt_tasks_wcrt, et_tasks_wcrt, et_tasks_sched)

        # print(f"tt: {TT_tasks_WCRT} et: {ET_tasks_WCRT} et_schedule: {ET_schedule}")
        print(f"Candidate cost: {int(candidate_cost)}")

        if candidate_cost < parameters.best_cost:  # update the best solution for lower cost
            parameters.best_cost = candidate_cost
            parameters.best_solution = candidate_solution
            parameters.best_schedule=tt_schedule

        else:
            print("candidate has a worse solution than the best solution")
            candidate_cost_norm=np.interp(candidate_cost,[1,parameters.norm_max],[0,200])
            best_cost_norm=np.interp(parameters.best_cost,[1,parameters.norm_max],[0,200])
            rand_number=np.random.rand()
            factor_prob=np.exp(-(candidate_cost_norm - best_cost_norm)/parameters.curr_temp)
            print("DECISION FACTORS",rand_number,factor_prob)
            print(f"Temperature:{parameters.curr_temp}")
            if (rand_number < factor_prob  ):
                print("candidate with worse solution was accepted")
                print(f"Candidate cost: {candidate_cost} and Best cost: {parameters.best_cost} before random acceptance")
                parameters.best_cost = candidate_cost
                parameters.best_solution = candidate_solution
                parameters.best_schedule=tt_schedule


        parameters.curr_temp = parameters.curr_temp/(1+parameters.cool*parameters.iter)
    
    # return the new random changes to have the next candidates
    # we are still going to discuss the boundaries
    # define limits for generated variables
    max_number_poll_servers = 4
    max_budget_variation = 100
    max_period_variation = 300
    max_number_poll_servers_variation = 2

    number_poll_servers=1

    #number_poll_servers_variation = np.random.randint(-max_number_poll_servers_variation,max_number_poll_servers_variation, 1)
    budget_poll_servers=-1

    while(budget_poll_servers<1):
        budget_poll_servers_variation = np.random.randint(-max_budget_variation, max_budget_variation, size=1)
        budget_poll_servers = parameters.best_solution[1] + budget_poll_servers_variation

    period_poll_servers=hyperperiod-1
    while(hyperperiod%period_poll_servers!=0 or period_poll_servers<1):
        period_poll_servers_variation = np.random.randint(-max_period_variation, max_period_variation, size=1)
        period_poll_servers = parameters.best_solution[2] + period_poll_servers_variation
        if(period_poll_servers==0): period_poll_servers=-1
    return int(number_poll_servers), int(budget_poll_servers), int(period_poll_servers)