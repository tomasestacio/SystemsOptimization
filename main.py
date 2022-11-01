import pandas as pd
import numpy as np
import random
from math import gcd

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

# set file path for test cases
testcases_path = "/Users/joaomena/Documents/test_cases"

# set default values for SA temperature and cooling
def_temp = 1
def_cooling = 0.25

# set default polling server parameters
def_no_server = 1
def_budget = 300
def_period = 1200


class Task:
    """
    class used to represent tasks imported from the test cases
    """

    def __init__(self, task_dict):
        self.name = task_dict['name']
        self.duration = task_dict['duration']
        self.period = task_dict['period']
        self.type = task_dict['type']
        self.priority = task_dict['priority']
        self.deadline = task_dict['deadline']


class SimAnnealingParams:
    """
    class used to define parameters used in the SA algorithm
    """

    def __init__(self, temperature, solution, cost, cooling_factor, number_poll_servers, budget_poll_servers,
                 period_poll_servers):
        self.curr_temp = temperature
        self.cool = cooling_factor
        self.best_solution = solution
        self.best_cost = cost
        self.number_poll_servers = number_poll_servers
        self.budget_poll_servers = budget_poll_servers
        self.period_poll_servers = period_poll_servers


def tasks_parser(path):
    """
    get all tasks from the .csv files in the testcases folder and return them as objects in a list
    :param path: path to test cases file
    :return: list of Task objects with all tasks found
    """

    df = pd.read_csv(
        f'{path}/inf_10_10/taskset__1643188013-a_0.1-b_0.1-n_30-m_20-d_unif-p_2000-q_4000-g_1000-t_5__0__tsk.csv',
        sep=';').to_dict(orient="index")  # read single .csv file and separate columns by ';'
    task_list = []
    for task in df:
        task_list.append(Task(df[task]))

    return task_list


def divisible_random(a, b, n):
    if b - a < n:
        raise Exception('{} is too big'.format(n))
    result = random.randint(a, b)
    while result % n != 0:
        result = random.randint(a, b)
    return result


def dbf(t, t_list):
    """
    compute Demand Bound Function
    :param t: time instant
    :param t_list: task list
    :return: result of the mathematical operation
    """
    s = 0
    for task in t_list:
        if task.type == "ET":
            continue
        s += ((t + task.period - task.deadline) / task.period) * task.duration
    return s


def pdc(t_list, tt_hyperperiod):
    """
    use processor demand criterion to determine if a set of tasks is schedulable or not
    :param t_list: array of tasks to consider
    :param tt_hyperperiod: hyperperiod from the tasks considered
    :return: 0 if schedulable, 1 if not schedulable
    """
    sched = 0
    t = 1
    while t < tt_hyperperiod:
        s = dbf(t, t_list)
        if s > t:
            sched += 1
        t += 1
    return sched


def edf_sim(tt, ps_array):
    """
    shedule time triggered tasks and compute worst case response time
    :param tt: array with time triggered tasks
    :param ps_array: array with polling servers
    :return: arrays with schedule made and worst case response time and hyperperiod
             or empty arrays if schedule is unfeasible within the deadline
    """
    # add tt tasks to array
    tt_tasks = tt

    # define arrays for computational time (C), deadline (D) and period (P)
    C = []
    D = []
    p = []
    U = 0

    # fill arrays with parameters from all tasks
    for task in tt_tasks:
        C.append(task.duration)
        D.append(task.deadline)
        p.append(task.period)
        U = U + task.duration / task.period

    # add polling servers to tt tasks array
    for ps in ps_array:
        tt_tasks.append(ps)
        C.append(ps.duration)
        D.append(ps.deadline)
        p.append(ps.period)
        U = U + ps.duration / ps.period

    # compute hyperperiod
    T = np.lcm.reduce(p)
    print(f"Hyperperiod: {T}")

    # initialize arrays of set length for r and wcrt
    r = np.zeros(len(tt_tasks))
    wcrt = np.zeros(len(tt_tasks))
    wcrt_changed = np.zeros(len(tt_tasks))

    # check if TT tasks are schedulable for EDF using processor demand criterion
    """
    tt_valid = pdc(tt_tasks, T)
    if tt_valid > 0:
        print("Task set not schedulable")
        return [], [], T
    """

    sigma = []
    t = 0
    # We go through each slot in the schedule table until T
    while t < T:
        state = 0
        i = 0
        for task in tt_tasks:
            if task.duration > 0 and task.deadline <= t:
                print('Deadline miss!')
                return [], [], T

            if t % task.period == 0:
                wcrt_changed[i] = 0
                r[i] = t
                task.duration = C[i]
                task.deadline = t + D[i]

            i += 1
        # print("tt_tasks gone through")

        for task in tt_tasks:
            if task.duration != 0:
                # there are still tasks that have computation time
                state = 1
                break
        # print("state checked")

        if state == 1:
            edf_name = edf(tt_tasks)
            sigma.append(edf_name)
            i = 0
            for task in tt_tasks:
                if edf_name == task.name:
                    task.duration -= 1

                if task.duration == 0 and task.deadline >= t and wcrt_changed[i] == 0:
                    if (t - r[i]) >= wcrt[i]:  # Check if the current WCRT is larger than the current maximum.
                        wcrt[i] = t - r[i]
                        wcrt_changed[i] = 1
                i += 1

        elif state == 0:
            sigma.append("idle")

        t += 1

    for task in tt_tasks:
        if task.duration > 0:
            print("Schedule is infeasible")
            return [], [], T

    print(f"tt wcrt: {wcrt}")
    return sigma, wcrt, T


def edf(tt_tasks):
    """
    get the name of the task with the earliest absolute deadline
    :param tt_tasks: array of tasks to consider
    :return: name of the task with the earliest absolute deadline
    """
    trade = 99999999999  # largest int number possible
    for task in tt_tasks:
        if trade > task.deadline and task.duration != 0:
            trade = task.deadline
            name = task.name
    return name


def et_schedule(task_list, Cp, Tp, Dp):
    """
    determine if event triggered tasks are schedulable and compute worst case response time
    :param task_list: list of tasks
    :param Cp: compute time
    :param Tp: period
    :param Dp: deadline
    :return: bool for schedulability and tuple with worst case response times
    """
    et_mask = []
    for task in task_list:
        et_mask.append((task.type == 'ET'))

    et_tasks = [task for task, y in zip(task_list, et_mask) if y]

    delta = Tp + Dp - 2 * Cp  # in the future this is a parameter (extension 3)
    alfa = Cp / Tp

    period_list = []
    for task in et_tasks:
        period_list.append(task.period)
    hyperperiod = np.lcm.reduce(period_list)  # compute hyperperiod

    response_time = []
    for index, actual_task in zip(range(len(et_tasks)), et_tasks):
        t = 0  # current time
        response_time.append(actual_task.deadline + 1)
        # Initialize the response time of τi to a value exceeding the deadline
        # because if it's not schedulable, it is already done to return False

        while t <= hyperperiod:

            # linear supply bound function that will be important to compute the WCRT
            supply = alfa * (t - delta)
            if supply < 0:
                supply = 0

            # get subset of ET tasks that have higher priority than the current ET task
            demand = 0
            demand_tasks = []
            for task in et_tasks:
                if task.priority >= actual_task.priority:
                    demand_tasks.append(task)

            for task in demand_tasks:
                demand = demand + t * task.duration / task.period

            if supply >= demand and supply != 0:  # if supply >=demand , we found the response time
                response_time[index] = t
                break

            t += 1

        if response_time[index] > actual_task.deadline:
            return False, response_time
    print(f"et wcrt: {response_time}")
    return True, response_time


def cost_function(tt_wcrt, et_wcrt, et_sched):
    """
    compute cost function to determine quality of a solution
    :param tt_wcrt: time triggered tasks worst case response time
    :param et_wcrt: event triggered tasks worst case response time
    :param et_sched: event triggered tasks schedulability
    :return: int value of computed cost
    """
    if len(tt_wcrt) == 0 or len(et_wcrt) == 0 or et_wcrt[0] == 0:
        return 999999999999
    num_et = len(et_wcrt)
    num_et = len(et_wcrt)

    coefficient = 20

    sum_tt = 0
    for i in tt_wcrt:
        sum_tt += i

    sum_et = 0
    for i in et_wcrt:
        sum_et += i

    # if the schedule for ET tasks is not possible, it will have a huge impact in the cost
    cost = sum_tt / len(tt_wcrt) + sum_et * (1 + et_sched * coefficient) / len(et_wcrt)

    return cost


def create_poll_src(no_srv, budget, period):
    """
    create polling server with given parameters
    :param no_srv: number of intended polling servers
    :param budget: budget for the polling server
    :param period: period for the polling server
    :return: list of polling servers created
    """
    ps_matrix = []
    i = 0
    while i < no_srv:
        ps_def_aux = {'name': "tPS{0}".format(i + 1), 'duration': budget, 'period': period, 'type': "TT", 'priority': 7,
                      'deadline': period}
        ps_def = Task(ps_def_aux)
        ps_matrix.append(ps_def)
        i += 1

    return ps_matrix


def simulated_annealing(tt_tasks_wcrt, et_tasks_wcrt, et_tasks_sched, candidate_solution, parameters, hyperperiod):
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
    # calculate cost with the parameters given
    candidate_cost = cost_function(tt_tasks_wcrt, et_tasks_wcrt, et_tasks_sched)

    # define limits for generated variables
    max_number_poll_servers = 4
    max_budget = 500
    min_budget = 2
    min_period = 2
    max_period = 12000
    max_budget_variation = 100
    max_period_variation = 300

    # print(f"tt: {TT_tasks_WCRT} et: {ET_tasks_WCRT} et_schedule: {ET_schedule}")
    print(f"Candidate cost: {candidate_cost}")

    if candidate_cost < parameters.best_cost:  # update the best solution for lower cost
        parameters.best_cost = candidate_cost
        parameters.best_solution = candidate_solution

    else:
        if np.random.rand() < np.exp(-(candidate_cost - parameters.best_cost) / parameters.curr_temp):
            print(f"Candidate cost: {candidate_cost} and Best cost: {parameters.best_cost} before else")
            parameters.best_cost = candidate_cost
            parameters.best_solution = candidate_solution

    # reduce the temperature (we are still going to discuss this)
    parameters.curr_temp = parameters.cool * parameters.curr_temp

    # return the new random changes to have the next candidates
    # we are still going to discuss the boundaries
    """
    number_poll_servers = np.random.randint(1, max_number_poll_servers, 1)

    budget_poll_servers = np.random.randint(min_budget, max_budget, size=1)

    period_poll_servers = np.random.randint(min_period, max_period, size=1)
    """
    parameters.number_poll_servers = 1
    # budget_poll_servers = divisible_random(min_budget, max_budget, 5)
    # period_poll_servers = divisible_random(budget_poll_servers, max_period, 1000)

    max_number_poll_servers_variation = 2

    number_poll_servers_variation = np.random.randint(-max_number_poll_servers_variation,
                                                      max_number_poll_servers_variation, 1)

    budget_poll_servers_variation = np.random.randint(-max_budget_variation, max_budget_variation, size=1)

    period_poll_servers_variation = np.random.randint(-max_period_variation, max_period_variation, size=1)

    # number_poll_servers=max(1,parameters.number_poll_servers+number_poll_servers__variation)

    parameters.budget_poll_servers = max(100 + abs(budget_poll_servers_variation), parameters.budget_poll_servers +
                                         budget_poll_servers_variation)

    # parameters.period_poll_servers = max(100, parameters.period_poll_servers + period_poll_servers_variation)

    return parameters.number_poll_servers, parameters.budget_poll_servers, parameters.period_poll_servers


def main():
    # create list with an object Task for every task in  the csv files
    task_list = tasks_parser(testcases_path)

    # create list of time triggered tasks
    tt_list = []
    for task in task_list:
        if task.type == "TT":
            tt_list.append(task)

    # schedule  ET and TT tasks
    tt_schedule, tt_wcrt, tt_hyperperiod = edf_sim(tt_list, create_poll_src(def_no_server, def_budget, def_period))
    et_bool, et_wcrt = et_schedule(task_list, def_budget, def_period, def_period)

    # set simulated annealing initial parameters
    cand_sol = [def_no_server, def_budget, def_period]
    params = SimAnnealingParams(def_temp, cand_sol, cost_function(tt_wcrt, et_wcrt, et_bool), def_cooling,
                                def_no_server, def_budget, def_period)
    print(f"Initial cost: {params.best_cost}")

    for i in range(0, 100):
        # run simulated annealing
        print(f"Iteration {i}")
        new_no_ps, new_budget, new_period = simulated_annealing(tt_wcrt, et_wcrt, et_bool, cand_sol, params,
                                                                tt_hyperperiod)
        print(f"Iteration {i} SA executed with budget of {new_budget} and period of {new_period}")
        print(f"Best cost: {params.best_cost}")

        # update parameters

        cand_sol = [new_no_ps, new_budget, new_period]
        new_ps = create_poll_src(1, new_budget, new_period)
        tt_schedule, tt_wcrt, tt_hyperperiod = edf_sim(tt_list, new_ps)
        et_bool, et_wcrt = et_schedule(task_list, new_budget, new_period, new_period)

    print(params.best_solution)


if __name__ == "__main__":
    main()
