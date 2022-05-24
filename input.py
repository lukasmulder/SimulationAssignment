# File for input analysis
from helper import import_from_csv
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# connection_time = list(zip(range(0,71) , import_from_csv("connection_time.csv") ) )
# arrival_hours = list(zip(range(0,24) ,import_from_csv("arrival_hours.csv") ) )
# charging_volume = list(zip(range(0,102) ,import_from_csv("charging_volume.csv") ) )

# initial exploration

connection_time = import_from_csv("connection_time.csv")
charging_volume = import_from_csv("charging_volume.csv")

# plt.subplot(2,2,1)
# plt.scatter(range(0,71), connection_time)
# plt.xlabel("connection time in hours")
# plt.ylabel("fraction of cars")
#
# plt.subplot(2,2,2)
# plt.scatter(range(0,102), charging_volume)
# plt.xlabel("charging volume in kWh")
# plt.ylabel("fraction of cars")
#
# plt.subplot(2,2,3)
# plt.plot(range(0,71), connection_time)
# plt.xlabel("connection time in hours")
# plt.ylabel("fraction of cars")
#
# plt.subplot(2,2,4)
# plt.plot(range(0,102), charging_volume)
# plt.xlabel("charging volume in kWh")
# plt.ylabel("fraction of cars")

# judging by the scatter plots, the following distributions seem plausible:
# connection_time: Exponential, Gamma with K < 1
# charging_volume:- Weibull, lognormal

# CONNECTION TIME
# x = range(0,71)

# Gamma distribution
# p, loc, scale = stats.gamma.fit(connection_time) # fit is not accurate
# p, loc, scale = 0.5, 0, 20
# #plt.subplot(1,2,1)
# plt.plot(x, stats.gamma.pdf(x, p, loc, scale))
# plt.scatter(x, connection_time)
# plt.xlabel("Gamma")

# for i in range(0,6):
#     p, loc, scale = 0.5, 0, 10
#     plt.subplot(2,3,i+1)
#     plt.plot(x, stats.gamma.pdf(x, p + 0.1*i, loc, scale))
#     plt.scatter(x, connection_time, s = 1)
#     plt.xlabel("Gamma {}".format(p + 0.1*i) )


# Exponential distribution
# loc, scale = stats.expon.fit(connection_time)
# print(loc, scale)
# loc, scale = 0, 10
# #plt.subplot(1,2,2)
# plt.plot(x, stats.expon.pdf(x, loc, scale))
# plt.scatter(x, connection_time)
# plt.xlabel("Exponential")

# CHARGING TIME
x = range(0,102)

# lognormal distribution
p, loc, scale = stats.lognorm.fit(charging_volume) # fit is not accurate
p, loc, scale = 0.5, 0, 20
plt.subplot(1,2,1)
plt.plot(x, stats.lognorm.pdf(x, p, loc, scale))
plt.scatter(x, charging_volume)
plt.xlabel("Lognormal")

# for i in range(0,6):
#     p, loc, scale = 0.5, 0, 10
#     plt.subplot(2,3,i+1)
#     plt.plot(x, stats.lognorm.pdf(x, p + 0.1*i, loc, scale))
#     plt.scatter(x, charging_volume, s = 1)
#     plt.xlabel("Lognormal {}".format(p + 0.1*i) )


# Weibull distribution
p, loc, scale = stats.weibull_min.fit(charging_volume)
p, loc, scale = 1.2, 0, 15
plt.subplot(1,2,2)
plt.plot(x, stats.weibull_min.pdf(x, p, loc, scale))
plt.scatter(x, charging_volume)
plt.xlabel("Weibulll")

plt.show()
