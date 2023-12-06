import numpy as np
import simpy
import pandas as pd
from componets import Cinema, Customer
from utils import time_to_seconds, maximum_at_intervals, extend_arrays

np.random.seed(2510)

#Настройки симуляции всё время указано в секундах
N_tickets_desk = 10
T_tickets = 45
N_security = 10
T_security = 60
N_rooms = 4
T_rooms_entarance = 20
SIM_TIME = 3600 * 5

T_before_start = 15 #в минутах
T_before_diviation = 5 #в минутах
OPEN_TIME = "15:00" #время открытия, совпадает с начальной точкой по времени симуляции
open_time_seconds = time_to_seconds(OPEN_TIME)


print("Simulation starts")
 #функция создаёт всех посетителей, которые должны придти
customers = Customer.generate_customers(pd.read_csv('movies.csv'), OPEN_TIME, T_before_start, T_before_diviation)
env = simpy.Environment()
cinema = Cinema(env, N_tickets_desk, T_tickets, N_security, T_security, N_rooms, T_rooms_entarance)
for customer in customers:
    env.process(customer.enter(env, cinema))
env.run(until=SIM_TIME)
print("Simulation ends")


print("\nSimulation Report")
print(f"Peoples served:{cinema.people_served}")
print(f"Average waiting time:{np.average(cinema.waiting_time)}")


import matplotlib.pyplot as plt

ticket_x, ticket_y = maximum_at_intervals(cinema.tickets_queue, 900, open_time_seconds)
security_x, security_y = maximum_at_intervals(cinema.security_queue, 900, open_time_seconds)
room_x, room_y = maximum_at_intervals(cinema.room_queue, 900, open_time_seconds)

extend_arrays([ticket_x, ticket_y], [security_x, security_y], [room_x, room_y])

plt.plot(ticket_x, ticket_y, label = 'Очередь на кассах')
plt.plot(security_x, security_y, label = 'Очередь на охране')
plt.plot(room_x, room_y, label='Очередь перед залом')

plt.legend()
plt.savefig('result.png')
plt.show()