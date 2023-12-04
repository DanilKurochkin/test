import numpy as np
import simpy
import pandas as pd
from utils import timeToSeconds, generate_customers, get_intervals, maximum_at_intervals

np.random.seed(25)

#Настройки симуляции всё время указано в секундах
N_tickets_desk = 10
T_tickets = 45
N_security = 10
T_security = 60
N_rooms = 4
T_rooms_entarance = 20
SIM_TIME = 3600 * 4

T_before_start = 15 #в минутах
T_before_diviation = 5 #в минутах
OPEN_TIME = "15:00" #время открытия, совпадает с начальной точкой по времени симуляции
open_time_seconds = timeToSeconds(OPEN_TIME)

#списоки с изменениями в длине очереди внутри содержит список [длина_очереди, время_изменения]
tickets_queue = [] 
security_queue = []
room_queue = []

#список со временем ожидания посетителя
waiting_time = []

#текущая длина очереди
current_tickets_queue = 0 
current_security_queue = 0
current_room_queue = 0
people_served = 0


class Cinema():
    def __init__(self, env : simpy.Environment, N_tickets_deck, T_tickets, N_security, T_security, N_rooms, T_rooms_entarance):
        self.env = env
        self.N_tickets_desk = simpy.Resource(env, N_tickets_deck)
        self.T_tickets = T_tickets
        self.N_security = simpy.Resource(env, N_security)
        self.T_security = T_security
        self.N_rooms = simpy.Resource(env, N_rooms)
        self.T_rooms_entarance = T_rooms_entarance
        
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
def customer(env : simpy.Environment, customer_name : str, cinema : Cinema):
    global tickets_queue, security_queue, room_queue
    global current_tickets_queue, current_room_queue, current_security_queue
    global people_served
    
    print(f'Customer {customer_name} enters cinema at {env.now:.2f}')
    start = env.now
    with cinema.N_tickets_desk.request() as request:
        current_tickets_queue += 1
        tickets_queue.append([current_tickets_queue, env.now])
        yield request
        print(f'CASHIER:Customer {customer_name} start buying a ticket')

        yield env.process(cinema.buy_tickets(customer_name))        
        print(f'CASHIER:Customer {customer_name} buyed tickets')
        current_tickets_queue -= 1
        tickets_queue.append([current_tickets_queue, env.now])
    
    with cinema.N_security.request() as request:
        current_security_queue += 1
        security_queue.append([current_security_queue, env.now])
        yield request
        print(f'SECURITY:Customer {customer_name} start security look up')
        
        yield env.process(cinema.security_lookup(customer_name))
        print(f'SECURITY:Customer {customer_name} pass throw security post')
        current_security_queue -= 1
        security_queue.append([current_security_queue, env.now])
    
    with cinema.N_rooms.request() as request:
        current_room_queue += 1
        room_queue.append([current_room_queue, env.now])
        yield request
        print(f'ENTER:Customer {customer_name} entering room')
        
        yield env.process(cinema.room_entarance(customer_name))
        
        print(f'ENTER:Customer {customer_name} served')
        current_room_queue -= 1
        room_queue.append([current_room_queue, env.now])
    
    end = env.now
    waiting_time.append(end - start)
    people_served += 1

def setup(env : simpy.Environment, N_tickets_deck, T_tickets, N_security, T_security, N_rooms, T_rooms_entarance):
    cinema = Cinema(env, N_tickets_deck, T_tickets, N_security, T_security, N_rooms, T_rooms_entarance)

    i = 0
    while True:
        if i < len(intervals):
            yield env.timeout(intervals[i]) #сначала были сгенирированы все потенциальные гости со временем их прибытия, затем вычислены интервалы между гостями
            env.process(customer(env, customers[i][1], cinema))
            i += 1
        else:
            break
        
customers = generate_customers(pd.read_csv('movies.csv'), OPEN_TIME, T_before_start, T_before_diviation) #функция создаёт всех посетителей, которые должны придти
intervals = get_intervals(customers) #вычисляет интервал прихода между двумя близжайшими по времени посетителями

print("Simulation starts")

env = simpy.Environment()
env.process(setup(env, N_tickets_desk, T_tickets, N_security, T_security, N_rooms, T_rooms_entarance))
env.run(until=SIM_TIME)

print("Simulation ends")

import matplotlib.pyplot as plt

ticket_x, ticket_y = maximum_at_intervals(tickets_queue, 900, open_time_seconds)
security_x, security_y = maximum_at_intervals(security_queue, 900, open_time_seconds)
room_x, room_y = maximum_at_intervals(room_queue, 900, open_time_seconds)

plt.plot(ticket_x, ticket_y, label = 'Очередь на кассах')
plt.plot(security_x, security_y, label = 'Очередь на охране')
plt.plot(room_x, room_y, label='Очередь перед залом')

plt.legend()
plt.savefig('result.png')
plt.show()