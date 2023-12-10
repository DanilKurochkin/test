import numpy as np
import pandas as pd

def seconds_to_time(seconds : float) -> str: #перевод времени в часы форамата '03:14'
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    return f'{int(hours):02}:{int(minutes):02}'

def time_to_seconds(time : str) -> float: #перевод времени из формата '03:14' в секунды
    nums = time.split(sep = ':')
    result = int(nums[0])*3600 + int(nums[1])*60
    
    return result

def maximum_at_intervals(data ,interval : float, end, open_time = 0) -> (list[str], list[float]): #максимум на заданном интервале
    start = 0
    x = []
    y = []
    
    while start < end:
        x.append(seconds_to_time(start + open_time))
        #получим максимальную длину очереди на заданном интервале
        in_interval = list(filter(lambda x: start + interval > x[1] and x[1] >= start, data))
        if len(in_interval) == 0:
            y.append(0)
        else:
            new_value = max(in_interval, key=lambda x: x[0])[0]
            y.append(new_value)
        start += interval
    
    return x, y