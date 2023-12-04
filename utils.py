import numpy as np
import pandas as pd

def secondsToTime(seconds : float) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    return f'{hours:02}:{minutes:02}'

def timeToSeconds(time : str) -> float:
    nums = time.split(sep = ':')
    result = int(nums[0])*3600 + int(nums[1])*60
    
    return result

def generate_customers(df : pd.DataFrame, OPEN_TIME, T_before_start, T_before_diviation) ->  list:
    customers = []
    
    seconds_open = timeToSeconds(OPEN_TIME)
    for i in range(len(df)):
        data_string = df.iloc[i]
        seconds_start = timeToSeconds(data_string['start_time'])
        for j in range(data_string['total_viewers']):
            arrival_time = max(0, np.random.normal(loc=seconds_start - seconds_open - T_before_start * 60,
                                                   scale=T_before_diviation * 60))
            name = f'number№{j} to movie №{data_string["movie_number"]}'
            customers.append([arrival_time, name])
    
    customers.sort(key=lambda x:x[0])
    return customers

def get_intervals(customers : list) -> list[float]:
    intervals = []
    intervals.append(customers[0][0])
    
    for i in range(1, len(customers)):
        intervals.append(customers[i][0] - customers[i-1][0])
    
    return intervals