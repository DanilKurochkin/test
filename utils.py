import numpy as np
import pandas as pd

def secondsToTime(seconds : float) -> str: #перевод времени в часы форамата '03:14'
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    return f'{hours:02}:{minutes:02}'

def timeToSeconds(time : str) -> float: #перевод времени из формата '03:14' в секунды
    nums = time.split(sep = ':')
    result = int(nums[0])*3600 + int(nums[1])*60
    
    return result

def generate_customers(df : pd.DataFrame, OPEN_TIME, T_before_start, T_before_diviation) ->  list: #создаём всех посетителей, которые должные придти на заданные сеансы
    customers = []
    
    seconds_open = timeToSeconds(OPEN_TIME)
    for i in range(len(df)): #для каждого отдельного сеанса создаём зрителей, с учетом того, что они приходят не одновременно, и собираем их в один список
        data_string = df.iloc[i]
        seconds_start = timeToSeconds(data_string['start_time'])
        for j in range(data_string['total_viewers']):
            arrival_time = max(0, np.random.normal(loc=seconds_start - seconds_open - T_before_start * 60,
                                                   scale=T_before_diviation * 60)) 
            name = f'number№{j} to movie №{data_string["movie_number"]}'
            customers.append([arrival_time, name])
    
    customers.sort(key=lambda x:x[0]) #сортируем их по ожидаемому времени прибытия
    return customers

def get_intervals(customers : list) -> list[float]: #используя данные полученные выше, вычисляем интервалы между двумя близжайшими по времени прибытия зрителями
    intervals = []
    intervals.append(customers[0][0])
    
    for i in range(1, len(customers)):
        intervals.append(customers[i][0] - customers[i-1][0])
    
    return intervals

def maximum_at_intervals(data ,interval : float, open_time) -> (list[float], list[float]): #максимум на заданном интервале
    time = 0
    end = data[-1][1] // interval * interval + interval # округляем последнее время вверх, до числа кратному interval
    x = []
    y = []
    
    while time < end:
        #получим максимальную длину очереди на заданном интервале
        new_value = max(list(filter(lambda x: time + interval > x[1] and x[1] >= time, data)), key=lambda x: x[0])[0]
        x.append(secondsToTime(time + open_time))
        y.append(new_value)
        time += interval
    
    return x, y