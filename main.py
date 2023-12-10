import numpy as np
import simpy
import pandas as pd
from models import Cinema, Customer
from utils import time_to_seconds, maximum_at_intervals

#будем считать что в зал конкретный зал можно попасть только через определённое количество проходов, привязанных конкретно к этому сеансу
#если не очень понятно, то я имел ввиду, можете взглянуть на итоговый график, там сразу всё видно
#так же посчитаем количество опаздавших на своё кино
movies_schedule = pd.read_csv('movies.csv')
np.random.seed(2510)

#Настройки симуляции всё время указано в секундах
N_tickets_desk = 10 #количество касс
T_tickets = 10 #время обслуживания на кассе
N_security = 10 #количество охранных пропусков
T_security = 10 #время досмотра
N_room_entarance = 4 #количество входов в кинозал
T_rooms_entarance = 20 #время входа в кинозал
N_movies = len(movies_schedule) #количество фильмов в расписании
SIM_TIME = 3600 * 4 #длительность симуляции

T_before_start = 15 #среднее время прихода до фильма в минутах
T_before_diviation = 5 #стандартное отклонение времени прихода в минутах
OPEN_TIME = "15:00" #время открытия, совпадает с начальной точкой по времени симуляции
open_time_seconds = time_to_seconds(OPEN_TIME) #приведём время открытия к секунам


#Запуск симуляции
print("Simulation starts")
 #функция создаёт всех посетителей, которые должны придти
customers = Customer.generate_customers(movies_schedule, OPEN_TIME, T_before_start, T_before_diviation)
env = simpy.Environment()
cinema = Cinema(env, N_tickets_desk, T_tickets, N_security, T_security, N_room_entarance, T_rooms_entarance, N_movies)
for customer in customers:
    env.process(customer.enter(env, cinema))
env.run(until=SIM_TIME)
print("Simulation ends")

#Итоговые данные
print("\nSimulation Report")
print(f"Peoples served: {cinema.people_served}")
print(f"Latecomers: {cinema.latecomers}")
print(f"Average waiting time: {np.average(cinema.waiting_time)}")

import matplotlib.pyplot as plt

#получим максимумальную длину очередей на 15 минутных интервалах
ticket_x, ticket_y = maximum_at_intervals(cinema.tickets_queue, 900, SIM_TIME, open_time_seconds)
security_x, security_y = maximum_at_intervals(cinema.security_queue, 900, SIM_TIME, open_time_seconds)
room_x, room_y = maximum_at_intervals(cinema.room_queue, 900, SIM_TIME, open_time_seconds)

#итоговые графики
figure, (ax1, ax2) = plt.subplots(1, 2, figsize=(14,6))

ax1.plot(ticket_x, ticket_y, label = 'Очередь на кассах')
ax1.plot(security_x, security_y, label = 'Очередь на охране')
ax1.plot(room_x, room_y, label='Очередь перед залом (общая)')
ax1.tick_params(axis='x', rotation=90)
ax1.set_title('Очереди на проходных пунктах')
ax1.legend()

ax2.tick_params(axis='x', rotation=90)
for i in range(len(cinema.queue_room_per_movie)):
    x, y = maximum_at_intervals(cinema.queue_room_per_movie[i], 900, SIM_TIME, open_time_seconds)
    ax2.plot(x, y, label=f'Очередь на фильм №{i+1}')
ax2.set_title('Очереди в разные кинозалы')
ax2.legend()

plt.savefig('result.png')
plt.show()