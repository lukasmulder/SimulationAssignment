import random
import math
import csv
from numpy.random import choice
from pandas import read_csv
from state import update_flow, find_parents

# reads in a csv file
def import_from_csv(filename):
    #extracts second column from csv file and returns a list of floats
    data = read_csv(filename, sep = ";")

    info = data['Share of charging transactions'].tolist()

    return list(map(float, info))

# generates the next arrival time of a car
def generate_arrival_time(current_time, csv):
    time_hour = int(current_time/60 % 24)
    time_minute = current_time % 60
    extra_hours = 0

    rate = (750*csv["arrival"][time_hour]) / 60 # this function should give the rate of cars per minute
    p = random.random()
    arrival_time = - math.log(1 - p) / rate


    while arrival_time + time_minute > 60: # if we have a rate change (due to the next hour approaching), generate a new arrival time within the next hour
        time_minute = 0
        extra_hours += 1

        rate = (750*csv["arrival"][(time_hour + extra_hours) % 24]) / 60 # this function should give the rate of cars per minute
        p = random.random()
        arrival_time = - math.log(1 - p) / rate

    return (int(current_time/60) + extra_hours) * 60 + time_minute + arrival_time

# generates the charging volume and connection time using the csv files
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

    return charging_volume, connection_time

# normalize a list
def normalize(list):
    summ = sum(list)
    return [i/summ for i in list]

# generates 3 parking spaces that will be picked radnomly according to the distribution given.
def chooseparking():
    return choice([1,2,3,4,5,6,7], size = 3, replace = False, p=[0.15,0.15,0.15,0.2,0.15,0.1,0.1])

#returns the energy price for a given time
def convert_time_price(time):
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

#calculates starting time to minimize cost
def price_reduc_time(current_time, charging_volume, connection_time):
    #strategy is: if the price goes up: start now. Wait otherwise
    charging_time = charging_volume *10
    latest_start_time = current_time + connection_time - charging_time
    current_price = convert_time_price(current_time)

    #if the price will rise in the future
    if current_price == 16 or current_price == 18 :

        start_time = current_time #start now
    elif current_price == 20 or current_price == 22: #if the price goes down.

        #check if we can reach cheapest price at 00:00
        if latest_start_time -current_time >= 24*60 - (current_time%(24*60)):
            start_time = current_time + 24*60 - (current_time%(24*60))
        else: #otherwise start as late as possible
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

# geeft het echte optimum start tijd om prijs te minimalizeren
# gives the actual optimal start time to minimuze price
def good_price_reduc(current_time, charging_volume, connection_time):
    charging_time = charging_volume *10
    latest_start_time = current_time + connection_time - charging_time
    possible_times= possible_starttime(current_time, latest_start_time)

    maxprice = 100000
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

# calculates the revenue corresponding to a load pattern at each time.
def revenue(load_over_time):
    return list(map(lambda x : (x[0],x[1],convert_time_price(x[0])), load_over_time ) )

# formats the keys into for better labels
def rewrite_key(name):
    namelist = name.split(" vs ")
    firstname = namelist[0]
    secondname = namelist[1]

    output = []
    for current in [firstname,secondname]:
            splitfirst= current.split(']')

            #solar
            stringlist = splitfirst[0] +"]"
            if len(stringlist) == 2:
                solar = 0
            else:
                solar = len(stringlist.strip('][').split(','))

            #start
            strat = int(splitfirst[1][0])

            #season
            season = splitfirst[1][1]

            output.append([solar,strat,season])

    stringoutput = "("+str(output[0][0])+","+str(output[0][1])+","+output[0][2]+") vs ("+str(output[1][0])+","+str(output[1][1])+","+output[1][2]+")"

    return output, stringoutput

# formats a floating point to something that fits in a table.
def format_float(x):
    s = "{:.2f}".format(x)[0:6]
    if s[-1] == '.':
        s = s[:-1]
    return s
