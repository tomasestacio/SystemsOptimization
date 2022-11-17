import pandas as pd
import numpy as np
import random
import math
import logging
import os
import time

log_file = "project_results.log"
num = 1
if os.path.exists(log_file):
    while os.path.exists(f"project_results{num}.log"):
        num += 1
log_file = f"project_results{num}.log"
logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

# set file path for test cases
# testcases_path = r'C:\Users\tiago\code\git_repos\SystemsOptimization\testcases_seperation_tested'
testcases_path = "/Users/joaomena/Documents/testcases_seperation"
test_file = "inf_10_10/taskset__1643188013-a_0.1-b_0.1-n_30-m_20-d_unif-p_2000-q_4000-g_1000-t_5__0__tsk.csv"
# set default values for SA temperature and cooling
def_temp = 20
def_cooling = 0.5

# set default polling server parameters
def_no_server = 1
def_budget = 20
def_period = 25


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
        self.seperation = task_dict['seperation']


class SimAnnealingParams:
    """
    class used to define parameters used in the SA algorithm
    """

    def __init__(self, temperature, solution, cost, best_schedule, cooling_factor, norm_max):
        self.curr_temp = temperature
        self.cool = cooling_factor
        self.best_solution = solution
        self.best_cost = cost
        self.best_schedule = best_schedule
        self.iter = 1
        self.norm_max = norm_max


def tasks_parser(path, file):
    """
    get all tasks from the .csv files in the testcases folder and return them as objects in a list
    :param path: path to test cases file
    :return: list of Task objects with all tasks found
    """
    """
    df = pd.read_csv(
        f'{path}/inf_10_10/taskset__1643188013-a_0.1-b_0.1-n_30-m_20-d_unif-p_2000-q_4000-g_1000-t_5__0__tsk.csv',
        sep=';').to_dict(orient="index")  # read single .csv file and separate columns by ';' """

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


def pdc(t_list, tt_hyperperiod):
    """
    use processor demand criterion to determine if a set of tasks is schedulable or not
    :param t_list: array of tasks to consider
    :param tt_hyperperiod: hyperperiod from the tasks considered
    :return: 0 if schedulable, 1 if not schedulable
    """
    s = 0
    for task in t_list:
        s += (tt_hyperperiod / task.period) * task.duration

    if s > tt_hyperperiod:
        return 1

    return 0


def edf_sim(t_list, ps_array):
    """
    shedule time triggered tasks and compute worst case response time
    :param t_list: array with time all tasks
    :param ps_array: array with polling servers
    :return: arrays with schedule made and worst case response time and hyperperiod
             or empty arrays if schedule is unfeasible within the deadline
    """
    # define arrays for computational time (C), deadline (D) and period (P)
    C = []
    D = []
    p = []
    U = 0

    # add tt tasks to array and fill arrays with parameters from all tasks
    tt_list = []
    for task in t_list:
        if task.type == "TT":
            tt_list.append(task)
            C.append(task.duration)
            D.append(task.deadline)
            p.append(task.period)
            U = U + task.duration / task.period

    # add polling servers to tt tasks array
    for ps in ps_array:
        tt_list.append(ps)
        C.append(ps.duration)
        D.append(ps.deadline)
        p.append(ps.period)
        U = U + ps.duration / ps.period

    # compute hyperperiod
    T = np.lcm.reduce(p)
    print(f"Hyperperiod: {T}")

    # initialize arrays of set length for r and wcrt
    r = np.zeros(len(tt_list))
    wcrt = np.zeros(len(tt_list))
    wcrt_changed = np.zeros(len(tt_list))

    # check if TT tasks are schedulable for EDF using processor demand criterion
    tt_valid = pdc(tt_list, T)
    if tt_valid > 0:
        print("Task set not schedulable")
        return [], [], T
    print("Task set schedulable")

    # for task in tt_list:
    #     print(f"task {task.name}  duration {task.duration}  period {task.period}  deadline {task.deadline}")

    sigma = []
    t = 0
    # We go through each slot in the schedule table until T
    while t < T:
        state = 0
        i = 0
        for task in tt_list:
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

        for task in tt_list:
            if task.duration != 0:
                # there are still tasks that have computation time
                state = 1
                break
        # print("state checked")

        if state == 1:
            edf_name = edf(tt_list)
            sigma.append(edf_name)
            i = 0
            for task in tt_list:
                if edf_name == task.name:
                    task.duration -= 1

                if task.duration == 0 and task.deadline >= t and wcrt_changed[i] == 0 and edf_name == task.name:
                    if (t - r[i]) >= wcrt[i]:  # Check if the current WCRT is larger than the current maximum.
                        wcrt[i] = t - r[i]
                        wcrt_changed[i] = 1
                i += 1

        elif state == 0:
            sigma.append("idle")

        t += 1

    i = 0 
    for task in tt_list:
        if(C[i] > wcrt[i]):
            wcrt[i] = C[i]

        i += 1

        if task.duration > 0:
            print("Schedule is infeasible")
            return [], [], T


    # print(f"tt wcrt: {wcrt}")
    print(f"TRUE tt wcrt:{wcrt}")
    return sigma, wcrt, T



def edf(tt_tasks):
    """
    get the name of the task with the earliest absolute deadline
    :param tt_tasks: array of tasks to consider
    :return: name of the task with the earliest absolute deadline
    """
    trade = 99999999999  # largest int number possible
    name = ''
    for task in tt_tasks:
        if trade > task.deadline and task.duration != 0:
            trade = task.deadline
            name = task.name
    return name


def et_tasks_seperation(task_list, no_poll_srv):
    et_mask = []
    for task in task_list:
        et_mask.append((task.type == 'ET'))

    et_tasks = [task for task, y in zip(task_list, et_mask) if y]

    et_tasks_all_groups = []
    et_task_group = []
    for i in range(no_poll_srv):
        for task in et_tasks:
            if task.seperation == i + 1:
                et_task_group.append(task)
        et_tasks_all_groups.append(et_task_group)

    return et_tasks_all_groups


def et_schedule(et_tasks, Cp, Tp, Dp):
    """
    determine if event triggered tasks are schedulable and compute worst case response time
    :param et_tasks: list of tasks
    :param Cp: compute time
    :param Tp: period
    :param Dp: deadline
    :return: bool for schedulability and tuple with worst case response times
    """
    print(Cp)

    delta = Tp + Dp - 2 * Cp  # in the future this is a parameter (extension 3)
    alfa = Cp / Tp
    # print(f"alfa: {alfa}  delta: {delta}  Cp: {Cp}  Dp: {Dp}  Tp: {Tp}")

    period_list = []
    for task in et_tasks:
        period_list.append(task.period)
    hyperperiod = np.lcm.reduce(period_list)  # compute hyperperiod

    response_time = []

    for index, actual_task in zip(range(len(et_tasks)), et_tasks):
        t = 0  # current time
        response_time.append(actual_task.deadline + 1)
        # print(f"Response time: {response_time}")
        # print(f"Index: {index}")
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
            print("ET not schedulable")
            return False, response_time
    print(f"TRUE et wcrt: {response_time}")
    return True, response_time


def cost_function(tt_wcrt, et_wcrt_groups, et_sched):
    """
    compute cost function to determine quality of a solution
    :param et_wcrt_groups: event triggered tasks worst case response time
    :param tt_wcrt: time triggered tasks worst case response time
    :param et_sched: event triggered tasks schedulability
    :return: int value of computed cost
    """

    if len(tt_wcrt) == 0 or len(et_wcrt_groups) == 0:
        return 999999999999
    # num_et = len(et_wcrt)
    # num_et = len(et_wcrt)

    coefficient = 100
    sum_tt = 0
    for i in tt_wcrt:
        sum_tt += i
    print(f"tt cost: {sum_tt}")
    sum_et = 0
    for et_wcrt in et_wcrt_groups:
        for i in et_wcrt:
            sum_et += i
        # print("SUM_ET:",sum_et,len(et_wcrt_groups),et_sched)
    # print(f"et cost: {sum_et}")
    bool_var = et_sched
    # if the schedule for ET tasks is not possible, it will have a huge impact in the cost
    cost = sum_tt / len(tt_wcrt) + sum_et * (1 + 2 * bool_var * coefficient) / len(et_wcrt_groups)

    return cost


def create_poll_src(no_srv, budgets, periods):
    """
    create polling server with given parameters
    :param no_srv: number of intended polling servers
    :param budgets: budget for the polling server
    :param periods: period for the polling server
    :return: list of polling servers created
    """
    ps_matrix = []
    i = 0
    for budget, period in zip(budgets, periods):
        ps_def_aux = {'name': "tPS{0}".format(i + 1), 'duration': budget, 'period': period, 'type': "TT", 'priority': 7,
                      'deadline': period, 'seperation': 0}
        ps_def = Task(ps_def_aux)
        ps_matrix.append(ps_def)
        i += 1
    return ps_matrix


def simulated_annealing(tt_tasks_wcrt, et_tasks_wcrt, tt_schedule, et_tasks_sched, candidate_solution, parameters,
                        hyperperiod, tt_schedule_bool):
    """
    compares cost of proposed solution to the best solution and returns random values to test again
    :param tt_schedule: returned schedule from edf function
    :param tt_schedule_bool: bool that indicates if tt tasks are schedulable or not
    :param tt_tasks_wcrt: time triggered tasks worst case response time
    :param et_tasks_wcrt: event triggered tasks worst case response time
    :param et_tasks_sched: event triggered tasks schedulability
    :param candidate_solution: list of parameters that make up the solution
    :param parameters: SimulatedAnnealingParams object
    :param hyperperiod: hyperperiod of all time triggered tasks including polling server
    :return: new number of polling servers, budget and period randomly generated
    """

    # define limits for generated variables
    # max_number_poll_servers = 4
    max_budget_variation = 40
    max_period_variation = 50
    # max_number_poll_servers_variation = 2

    if tt_schedule_bool == 1:

        # calculate cost with the parameters given
        candidate_cost = cost_function(tt_tasks_wcrt, et_tasks_wcrt, et_tasks_sched)

        # print(f"tt: {TT_tasks_WCRT} et: {ET_tasks_WCRT} et_schedule: {ET_schedule}")
        print(f"Candidate cost: {int(candidate_cost)}")

        if candidate_cost < parameters.best_cost:  # update the best solution for lower cost

            parameters.best_cost = candidate_cost
            parameters.best_solution = candidate_solution
            parameters.best_schedule = tt_schedule
            logging.warning(
                f"NEW best cost for parameters in ITERATION: {parameters.iter}; NUM SERVERS: {candidate_solution[0]}; BUDGET: {candidate_solution[1]}; PERIOD: {candidate_solution[2]}\n"
                f"resulting in a BEST COST of {int(parameters.best_cost)}")

        else:
            print("candidate has a worse solution than the best solution")
            candidate_cost_norm = np.interp(candidate_cost, [1, parameters.norm_max], [0, 200])
            best_cost_norm = np.interp(parameters.best_cost, [1, parameters.norm_max], [0, 200])
            rand_number = np.random.rand()
            factor_prob = np.exp(-(candidate_cost_norm - best_cost_norm) / parameters.curr_temp)
            print("DECISION FACTORS", rand_number, factor_prob)
            print(f"Temperature:{parameters.curr_temp}")
            if rand_number < factor_prob:
                print("candidate with worse solution was accepted")
                print(
                    f"Candidate cost: {candidate_cost} and Best cost: {parameters.best_cost} before random acceptance")
                parameters.best_cost = candidate_cost
                parameters.best_solution = candidate_solution
                parameters.best_schedule = tt_schedule

        parameters.curr_temp = def_temp / (1 + parameters.cool * parameters.iter)

    # return the new random changes to have the next candidates
    # we are still going to discuss the boundaries

    number_poll_servers = candidate_solution[0]  # number of poll servers is fixed for the dataset

    period_poll_servers = []
    for i in range(number_poll_servers):
        period = hyperperiod - 1
        while hyperperiod % period != 0 or period < 1:
            period_poll_servers_variation = np.random.randint(-max_period_variation, max_period_variation, size=1)
            period = parameters.best_solution[2][i] + period_poll_servers_variation
            if period == 0:
                period = -1

        period_poll_servers.append(int(period))

    budget_poll_servers = []
    for i in range(number_poll_servers):
        budget = -1
        while budget < 1 or budget > period_poll_servers[i]:
            budget_poll_servers_variation = np.random.randint(-max_budget_variation, max_budget_variation, size=1)
            budget = parameters.best_solution[1][i] + budget_poll_servers_variation

        budget_poll_servers.append(int(budget))
    # print("BUDGET_POLL SERVERS:",budget_poll_servers)
    # print("PERIOD_POLL SERVERS:",period_poll_servers)
    return int(number_poll_servers), budget_poll_servers, period_poll_servers


def task_seperation(t_list):
    sep_list = []
    count = 0
    for task in t_list:
        if task.type == "ET":
            sep_list.append(task.seperation)
            count += 1

    # Find minimum number of polling servers from separation values
    unique_values = list(set(sep_list))
    min_no_ps = len(unique_values)

    # Find maximum number of polling servers from amount of ET tasks
    max_no_ps = count

    return max_no_ps, min_no_ps


def priority_parser(et_tasks):
    # reassignment of the priorities of the ET tasks according to the EDF method -> earliest deadline, biggest priority
    # 1) check the biggest deadline of the ET tasks in the test case
    # 2) divide that by the number of ET tasks in the test case
    # 3) assign priorities based on the space division
    max_deadline = 0

    for task in et_tasks:
        if max_deadline < task.deadline:
            max_deadline = task.deadline

    chunk_size = math.floor(max_deadline / 7)

    for task in et_tasks:
        for i in range(0, 7):
            if task.deadline - (i + 1) * chunk_size < 0:
                task.priority = i
                break

    return et_tasks


def main():
    # create list with an object Task for every task in  the csv files
    logging.info("Program started, setting initial conditions\n")
    task_list = []
    task_list = tasks_parser(testcases_path, test_file)

    not_sched_tt = 0
    not_sched_et = 0

    # get min / max number of polling servers
    max_no_srv, min_no_srv = task_seperation(task_list)  # we decided to use only the min_no_srv

    # get groups of et tasks with same separation number
    et_tasks_groups = et_tasks_seperation(task_list, min_no_srv)
    et_wcrt = []
    et_bool = 1
    et_wcrt_groups = []
    et_bool_groups = []
    budget_poll_srv = np.array([def_budget for i in range(min_no_srv)])
    period_poll_srv = np.array([def_period for i in range(min_no_srv)])

    # schedule  ET and TT tasks
    tt_schedule, tt_wcrt, tt_hyperperiod = edf_sim(task_list,
                                                   create_poll_src(min_no_srv, budget_poll_srv, period_poll_srv))
    if len(tt_wcrt) == 0:
        tt_schedule_bool = 0
        not_sched_tt += 1
    else:
        tt_schedule_bool = 1
        for i, et_tasks in enumerate(et_tasks_groups):
            et_bool, et_wcrt = et_schedule(et_tasks, def_budget, def_period, def_period)
            et_bool_groups.append(et_bool)
            et_wcrt_groups.append(et_wcrt)
    et_bool = 0
    for bool_var in et_bool_groups:
        if not bool_var:
            et_bool += 1
            not_sched_et += 1
            break

    # set simulated annealing initial parameters
    cand_sol = [min_no_srv, [def_budget for i in range(min_no_srv)], [def_period for i in range(min_no_srv)]]
    params = SimAnnealingParams(def_temp, cand_sol, cost_function(tt_wcrt, et_wcrt_groups, et_bool), tt_schedule,
                                def_cooling, 10000)

    print(f"Initial cost: {params.best_cost}")
    logging.info("Simulated Annealing starting.\n")
    logging.info(f"Using test case file: {testcases_path}/{test_file}")
    initial_time = time.time()
    curr_time = 0
    # params.curr_temp > 0.1
    while curr_time < 120:
        # run simulated annealing

        new_no_ps, new_budget, new_period = simulated_annealing(tt_wcrt, et_wcrt_groups, tt_schedule, et_bool, cand_sol,
                                                                params,
                                                                tt_hyperperiod, tt_schedule_bool)
        print(f"\nIteration {params.iter}")
        print(f"Iteration {params.iter} SA will be executed with budget of {new_budget} and period of {new_period}")
        print(f"Best cost: {int(params.best_cost)}")
        print("Best solution:", params.best_solution)

        params.iter = params.iter + 1
        # update parameters
        cand_sol = [new_no_ps, new_budget, new_period]
        new_ps = create_poll_src(new_no_ps, new_budget, new_period)
        tt_schedule, tt_wcrt, tt_hyperperiod = edf_sim(tasks_parser(testcases_path, test_file), new_ps)

        if len(tt_wcrt) == 0:
            tt_schedule_bool = 0
            not_sched_tt += 1
            continue
        else:
            tt_schedule_bool = 1
        # if TT set is not schedulable , it will not try to do et_schedule
        # for task in task_list:
        #    print(f"Name: {task.name}  Duration: {task.duration}  Period: {task.period}  Deadline: {task.deadline}")
        et_wcrt_groups = []
        et_bool_groups = []
        for i, et_tasks in enumerate(et_tasks_groups):
            et_bool, et_wcrt = et_schedule(et_tasks, new_budget[i], new_period[i], new_period[i])
            et_bool_groups.append(et_bool)
            et_wcrt_groups.append(et_wcrt)
        et_bool = 0
        for bool_var in et_bool_groups:
            if not bool_var:
                not_sched_et += 1
                et_bool += 1
        curr_time = time.time() - initial_time
        # et_bool, et_wcrt = et_schedule(tasks_parser(testcases_path), new_budget, new_period, new_period)

    logging.info(
        f"{params.iter} Iterations ran, of which {not_sched_tt} where not schedulable for TT and {not_sched_et}"
        f" were not schedulable for ET")
    print("No of Servers:", params.best_solution[0], ", Budget:", params.best_solution[1], ", Period:",
          params.best_solution[2])


if __name__ == "__main__":
    main()
