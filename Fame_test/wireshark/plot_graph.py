from cProfile import label
from click import style
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('R8-R5.csv')
data_2 = pd.read_csv('R8-R5-nodistribution.csv')

# Plot
plt.figure(figsize=(6.8, 4.2))
x = range(len(data['Interval start']))
plt.plot(x, data['All Packets'], label='With traffic Distribution')
# plt.xticks(x, data['Interval start'])

x = range(len(data_2['Interval start']))
plt.plot(x, data_2['All Packets'], label= 'W/O Traffic Distribution')
# plt.xticks(x, data_2['Interval start'])

plt.plot([0, 153], [1.5*10**6, 1.5*10**6], 'r:', alpha=0.5, label='Utilization Threshold')


# data = pd.read_csv('R7-R8.csv')
# data_2 = pd.read_csv('R7-R8-nodistribution.csv')
# # Plot
# plt.figure(figsize=(6.8, 4.2))
# x = range(len(data['Interval start']))
# plt.plot(x, data['All Packets'], label='With traffic Distribution')
# # plt.xticks(x, data['Interval start'])

# x = range(len(data_2['Interval start']))
# plt.plot(x, data_2['All Packets'], label= 'W/O Traffic Distribution')
# # plt.xticks(x, data_2['Interval start'])

plt.xlabel('Time (s)')
plt.ylabel('Bandwidth Used (bps)')

plt.legend()
plt.show()