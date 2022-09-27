import os
import csv
import glob
import pandas as pd
from asyncore import write

testcases_path = '/Users/joaomena/Documents/test_cases/'

def tasks_parser(testcases_path):
    """
    get all tasks from the .csv files in the testcases folder
    Arguments:
        (string) testcases_path - path to folder
    Returns:
        (class 'pandas.core.frame.DataFrame') df - dataframe with all tasks
    """
    sep = [';'] #csv column separator

    join_files = os.path.join(f"{testcases_path}/*/*.csv") #join all test case .csv files
    joined_list = glob.glob(join_files)

    df = pd.concat(map(pd.read_csv, joined_list), ignore_index=True) #read all .csv files into dataframe

    df.to_csv(f'{testcases_path}/tasks.csv', index=False) #export dataframe to single .csv file

    df = pd.read_csv(f'{testcases_path}/tasks.csv', sep=';') #read single .csv file and separate columns by ';'

    #redundancy caused by inability to separate columns directly on first read - hopefully can be fixed later

    return df

def main():
    pass

if __name__ == "__main__":
    main()