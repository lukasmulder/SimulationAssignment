from numpy.random import choice
import random
import math
import csv
from pandas import read_csv

def import_from_csv(filename):
    #extracts second column from csv file and returns a list of floats
    data = read_csv(filename, sep = ";")

    info = data['Share of charging transactions'].tolist()

    return list(map(float, info))

def generate_arrival_time(currenttime, csv):
    rate = (750*csv["arrival"][int(currenttime/60 % 24)]) / 60 # this function should give the rate of cars per minute
    p = random.random()
    arrival_time= -math.log(1 - p) / rate
    return currenttime + arrival_time

def generate_time(csv):
    #generates charging time and leaving time
    charging_size = choice(range(102), size = 1, replace = False, p=normalize(csv["charging"]))[0] #in kWh
    standing_time = choice(range(71),  size = 1, replace = False, p=normalize(csv["connection"]))[0] #in hours

    charging_time = charging_size / 6
    if charging_time > 0.7 * standing_time: #check the 70% rule
        standing_time = charging_time / 0.7

    return (charging_time*60,standing_time*60)

def normalize(list): #normalize a list
    summ = sum(list)
    return [i/summ for i in list]

def chooseparking():
    #generates 3 parking spaces that will be picked radnomly
    #parking spaces can be the same vgm willen wij dat niet
    return choice([1,2,3,4,5,6,7], size = 3, replace = False, p=[0.15,0.15,0.15,0.2,0.15,0.1,0.1])
