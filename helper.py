import random
import math
import csv
from numpy.random import choice
from pandas import read_csv
from state import update_flow, find_parents

def import_from_csv(filename):
    #extracts second column from csv file and returns a list of floats
    data = read_csv(filename, sep = ";")

    info = data['Share of charging transactions'].tolist()

    return list(map(float, info))

def generate_arrival_time(current_time, csv):
    time_hour = int(current_time/60 % 24)
    time_minute = current_time % 60
    rate = (750*csv["arrival"][time_hour]) / 60 # this function should give the rate of cars per minute
    p = random.random()
    arrival_time = - math.log(1 - p) / rate
    if arrival_time + time_minute > 60: # if we have a rate change (due to the next hour approaching), generate a new arrival time within the next hour
        rate = (750*csv["arrival"][(time_hour + 1) % 24]) / 60 # this function should give the rate of cars per minute
        p = random.random()
        arrival_time = - math.log(1 - p) / rate
        return current_time - time_minute + 60 + arrival_time # schedule the arrival time in the next hour.
    else:
        return current_time + arrival_time

def generate_time(csv):
    #generates charging volume and connection time
    charging_volume = choice(range(102), size = 1, replace = False, p=normalize(csv["charging"]))[0] + random.random() #in kWh
    connection_time = 60*choice(range(71),  size = 1, replace = False, p=normalize(csv["connection"]))[0] + 60*random.random()#in hours

    charging_time = 10 * charging_volume
    #check 70% rule
    delay = max(0, charging_time / 0.7 - connection_time)
    if delay > 0:
        #increase connection time
        connection_time = charging_time / 0.7

    return charging_volume, connection_time, delay

def normalize(list): #normalize a list
    summ = sum(list)
    return [i/summ for i in list]

def chooseparking():
    #generates 3 parking spaces that will be picked radnomly
    return choice([1,2,3,4,5,6,7], size = 3, replace = False, p=[0.15,0.15,0.15,0.2,0.15,0.1,0.1])

def convert_time_price(time): #returns the price for a given time
    time_hour = (time/60)%24
    if time_hour <8:
        return 16
    elif time_hour < 16:
        return 18
    elif time_hour <20:
        return 22
    else:
        return 20

#returns the size of the interval left
def convert_time_intervalleft(time):
    time_hour = (time/60)%24
    time_minutes = 60* time_hour
    if time_hour <8:
        return 8*60 -time_minutes
    elif time_hour <16:
        return 16*60 -time_minutes
    elif time_hour <20:
        return 20*60 -time_minutes
    else:
        return 24*60 - time_minutes


def price_reduc_time(current_time, charging_volume, connection_time): #calculates starting time to minimize cost
    #strategie is: als prijs naar boven gaat: nu beginnen, als prijs op tijd naar beneden gaat: wachtem
    charging_time = charging_volume *10
    latest_start_time = current_time + connection_time - charging_time
    current_price = convert_time_price(current_time)
    # print("\n\ncurrent time ", current_time)
    # print("connectio time ", connection_time)
    # print("current price ", current_price)
    # print("charging time ", charging_time)
    # print("latest start time ", latest_start_time)
    # print(current_time, charging_volume, connection_time)

    #als prijs omhoog gaat in toekomst
    if current_price == 16 or current_price == 18 :

        start_time = current_time #start now
    elif current_price == 20 or current_price == 22: #als prijs omlaag gaat

        #check if we can reach cheapest price at 00:00
        if latest_start_time -current_time >= 24*60 - (current_time%(24*60)):
            start_time = current_time + 24*60 - (current_time%(24*60))
        else: #anders zo laat mogelijk beginnen
            start_time = latest_start_time

    return start_time

#function that returns all possible starting times that could minimize price
def start_times_price_reduc(current_time, latest_start_time):
    interval_left = convert_time_intervalleft(current_time)
    #base case
    if interval_left > latest_start_time - current_time: #if we cannot reach next interval
        return [latest_start_time]
    else: #if we can reach next interval
        time_reached_later = start_times_price_reduc(current_time + interval_left, latest_start_time)
        time_reached_later.append(current_time+interval_left)
        return time_reached_later


#helper function to fix order
def possible_starttime(current_time, latest_start_time):
    possible_times= start_times_price_reduc(current_time, latest_start_time)
    possible_times.append(current_time)
    possible_times.reverse()
    return possible_times

#geeft het echte optimum start tijd om prijs teminimalizeren
def good_price_reduc(current_time, charging_volume, connection_time):
    charging_time = charging_volume *10
    latest_start_time = current_time + connection_time - charging_time
    possible_times= possible_starttime(current_time, latest_start_time)

    maxprice=100000
    besttime = 0
    for start_time in possible_times:
        price = price_if_starttime(start_time, charging_time)
        if price< maxprice:
            maxprice = price
            besttime = start_time

    return besttime


#function that calculcates the price for charging_time if we start charging at start time
#recursieve functie die steeds het blok toevoegt
def price_if_starttime(start_time, charging_time):
    if charging_time == 0:
        return 0
    current_price = convert_time_price(start_time)
    interval_time_left = convert_time_intervalleft(start_time)
    if interval_time_left < charging_time:
        return current_price*interval_time_left/60 + price_if_starttime(start_time + interval_time_left, charging_time - interval_time_left)
    else:
        return current_price*charging_time/60

def max_num_charging(loc):
    maxlist = [11,11,11,12,9,6,6]
    return maxlist[loc-1]

# Function takes a parking spot and checks if the network becomes overloaded
# if a flow change occurs at that parking spot.
def check_charging_possibility(cables, parking, flow_change):
    update_flow(cables, parking, flow_change) # simulate a flow change and test for overload in the network
    for id, cable in cables.items():
        if cable.flow > cable.capacity:
            update_flow(cables, parking, -flow_change) # remember to make the change undone
            return False
    update_flow(cables, parking, -flow_change) # remember to make the change undone
    return True

#function that checks if if alternative parking(later_parking) gets in the way of first parking in queue (first_parking)
#getting in the way means: having one of the cables on the path to first_parking reach full capacity
def check_skip_line(cables,first_parking, later_parking, flow_change):
    update_flow(cables, later_parking, flow_change)
    #check if any of the cables on route to first_parking is at more than capacity - 6
    path_to_first = find_parents(cables,first_parking)
    for i in path_to_first:
        cable= cables[i]
        if cable.flow > cable.capacity -6:
            update_flow(cables, later_parking, -flow_change) # remember to make the change undone
            return False
    update_flow(cables, later_parking, -flow_change) # remember to make the change undoneg
    return True

good_price_reduc(1,18*6,48*60)
