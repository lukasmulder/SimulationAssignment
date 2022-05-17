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
    charging_volume = choice(range(102), size = 1, replace = False, p=normalize(csv["charging"]))[0] #in kWh
    connection_time = choice(range(71),  size = 1, replace = False, p=normalize(csv["connection"]))[0] #in hours

    return (charging_volume,connection_time*60)

def normalize(list): #normalize a list
    summ = sum(list)
    return [i/summ for i in list]

def chooseparking():
    #generates 3 parking spaces that will be picked radnomly
    #parking spaces can be the same vgm willen wij dat niet
    return choice([1,2,3,4,5,6,7], size = 3, replace = False, p=[0.15,0.15,0.15,0.2,0.15,0.1,0.1])

def convert_time_price(time): #returns the price for a given time
    timehours = (time/60)%24
    if timehours <=8:
        return 16
    elif timehours <= 16:
        return 18
    elif timehours <= 20:
        return 22
    else:
        return 20
    
def price_reduc_time(current_time, charging_volume, connection_time): #calculates starting time to minimize cost
    #strategie is: als prijs naar boven gaat: nu beginnen, als prijs op tijd naar beneden gaat: wachtem
    charging_time = (charging_volume / 6) * 60
    latest_start_time = current_time +connection_time - charging_time
    current_price = convert_time_price(current_time)
    
    #als prijs omhoog gaat in toekomst
    if current_price== 16 or current_price== 18 :
        
        start_time = current_time #start now   
    elif current_price == 20 or current_price == 22: #als prijs omlaag gaat
        
        #check if we can reach cheapest price at 00:00
        if latest_start_time -current_time >= 24*60 - (current_time%(24*60)):
            start_time = current_time + 24*60 - (current_time%(24*60))
        else: #anders zo laat mogelijk beginnen
            start_time = latest_start_time
            
    return start_time
