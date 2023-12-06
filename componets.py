import simpy
import pandas as pd
from utils import time_to_seconds
import numpy as np

class Cinema():
    def __init__(self, env : simpy.Environment, N_tickets_deck, T_tickets, N_security, T_security, N_rooms, T_rooms_entarance):
        self.env = env
        self.N_tickets_desk = simpy.Resource(env, N_tickets_deck)
        self.T_tickets = T_tickets
        self.N_security = simpy.Resource(env, N_security)
        self.T_security = T_security
        self.N_rooms = simpy.Resource(env, N_rooms)
        self.T_rooms_entarance = T_rooms_entarance
        
        #списки для построения графиков и подсчёта метрик
        self.tickets_queue = []
        self.security_queue = []
        self.room_queue = []
        self.waiting_time = []
        self.length_tickets_queue = 0
        self.length_room_queue = 0
        self.length_security_queue = 0
        self.people_served = 0
        self.latecomers = 0

    #отладочные функции
    def buy_tickets(self, customer_name):
        yield self.env.timeout(self.T_tickets)
        print(f'Customer {customer_name} buyed tickets at {self.env.now:.2f}')
    
    def security_lookup(self, customer_name):
        yield self.env.timeout(self.T_security)
        print(f'Customer {customer_name} pass throw security at {self.env.now:.2f}')
    
    def room_entarance(self, customer_name):
        yield self.env.timeout(self.T_rooms_entarance)
        print(f'Customer {customer_name} pass in cinema at {self.env.now:.2f}')

#посетитель сначала идёт на кассу, затем на пост охраны, затем в зал
#когда он подходит к пункту, он записывается в очередь, когда он отходит - он из неё выписывается
class Customer():
    def __init__(self, name, arraival_time, movie_time):
        self.name = name
        self.arraival_time = arraival_time
        self.movie_time = movie_time
        
    def enter(self, env : simpy.Environment, cinema : Cinema):
        
        yield env.timeout(self.arraival_time)
        
        print(f'Customer {self.name} enters cinema at {env.now:.2f}')
        start = env.now
        with cinema.N_tickets_desk.request() as request:
            cinema.length_tickets_queue += 1
            cinema.tickets_queue.append([cinema.length_tickets_queue, env.now])
            yield request
            print(f'CASHIER:Customer {self.name} start buying a ticket')

            yield env.process(cinema.buy_tickets(self.name))        
            print(f'CASHIER:Customer {self.name} buyed tickets')
            cinema.length_tickets_queue -= 1
            cinema.tickets_queue.append([cinema.length_tickets_queue, env.now])
        
        with cinema.N_security.request() as request:
            cinema.length_security_queue += 1
            cinema.security_queue.append([cinema.length_security_queue, env.now])
            yield request
            print(f'SECURITY:Customer {self.name} start security look up')
            
            yield env.process(cinema.security_lookup(self.name))
            print(f'SECURITY:Customer {self.name} pass throw security post')
            cinema.length_security_queue -= 1
            cinema.security_queue.append([cinema.length_security_queue, env.now])
        
        with cinema.N_rooms.request() as request:
            cinema.length_room_queue += 1
            cinema.room_queue.append([cinema.length_room_queue, env.now])
            yield request
            print(f'ENTER:Customer {self.name} entering room')
            
            yield env.process(cinema.room_entarance(self.name))
            
            print(f'ENTER:Customer {self.name} served')
            cinema.length_room_queue -= 1
            cinema.room_queue.append([cinema.length_room_queue, env.now])
        
        end = env.now
        cinema.waiting_time.append(end - start)
        cinema.people_served += 1
        if end > self.movie_time:
            cinema.latecomers += 1
            print(f'!!!LATE:Customer {self.name} was late to movie')
    
    def generate_customers(df : pd.DataFrame, OPEN_TIME, T_before_start, T_before_diviation) ->  list['Customer']: #создаём всех посетителей, которые должные придти на заданные сеансы
        customers = []

        seconds_open = time_to_seconds(OPEN_TIME)
        for i in range(len(df)): #для каждого отдельного сеанса создаём зрителей, с учетом того, что они приходят не одновременно, и собираем их в один список
            data_string = df.iloc[i]
            seconds_start = time_to_seconds(data_string['start_time']) - seconds_open
            for j in range(data_string['total_viewers']):
                arrival_time = max(0, np.random.normal(loc=seconds_start - T_before_start * 60,
                                                        scale=T_before_diviation * 60)) 
                name = f'number№{j} to movie №{data_string["movie_number"]}'
                customers.append(Customer(name, arrival_time, seconds_start))

        return customers