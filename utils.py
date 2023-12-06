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

def maximum_at_intervals(data ,interval : float, open_time) -> (list[str], list[float]): #максимум на заданном интервале
    start = data[0][1] // interval * interval
    end = data[-1][1] // interval * interval + interval # округляем последнее время вверх, до числа кратному interval
    x = []
    y = []
    
    while start < end:
        #получим максимальную длину очереди на заданном интервале
        new_value = max(list(filter(lambda x: start + interval > x[1] and x[1] >= start, data)), key=lambda x: x[0])[0]
        x.append(seconds_to_time(start + open_time))
        y.append(new_value)
        start += interval
    
    return x, y

#нужно чтобы не было рваных графиков, в тех случайх когда на кассах уже давно пуста, а все изменения в очереди происходят на входе в кинозалы
def extend_arrays(*tuple_arrays : list[list[list, list]]) -> None:
    max_array = max(tuple_arrays, key=lambda x: len(x[0]))
    max_n = len(max_array[0])
    for array in tuple_arrays:
        if array is max_array:
            pass
        n = len(array[0])
        for i in range(n, max_n):
            array[1].append(0)
            array[0].append(max_array[0][i])