from state import State
from statistics import Statistics, update_statistics
from numpy.random import choice
import random
import math
import csv
from pandas import read_csv

class Event:
    def __init__(self, time, type, location=None):
        self.time = time
        self.type = type #"arrival", "finished charging", of "leave parking"
        self.location = location

def insert_event(event, eventQ):
    """Insert event in eventQ, and keep it sorted assuming it is sorted.
    If event an event has the same time as an event already in the eventQ,
    insert it to the right of the rightmost event.
    """
    low = 0
    high = len(eventQ)

    while low < high:
        mid = (low+high)//2
        if event.time < eventQ[mid].time:
            high = mid
        else:
            low = mid+1
    eventQ.insert(low, event)


def arrival(event, eventQ, parking, cables, network, csv):
    currenttime = event.time
    parkingchoices = chooseparking()
    for n in parkingchoices:
        if parking[n].free > 0:
            #park car
            parking[n].free-=1

            #charge car
            parking[n].charging+=1

            #update cables
            for cable in network[n]:
                cable.flow += 6

            ch,le = generate_time(csv)
            #schedule finished charging
            chargetime = currenttime + ch

            insert_event(Event(chargetime,"finished charging",n),eventQ)

            #schedule leave parking
            leavetime = currenttime + le
            insert_event(Event(leavetime,"leave parking",n),eventQ)

            break
        
    next_arrival_time = generate_arrival_time(currenttime, csv)
    insert_event(Event(next_arrival_time, "arrival"), eventQ)

def import_from_csv(filename):
    #extracts second column from csv file and returns a list of floats
    data = read_csv(filename, sep = ";")

    info = data['Share of charging transactions'].tolist()

    return list(map(float, info))

def generate_arrival_time(currenttime, csv):
    rate = (750*csv["arrival"][int(currenttime/60)]) / 60 # this function should give the rate of cars per minute
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

def finished_charging(event, eventQ, parking, cables, network,csv):
    loc = event.location #get the location where the car is parked
    for cable in network[loc]: #for every cable in the network that transports current to the car
        cable.flow -= 6 #reduce the flow by 6 kWh

def leave_parking(event, eventQ, parking, cables, network,csv):
    loc = event.location #get the location where the care was parked
    parking[loc].free += 1 #free up one space from the parking lot

#dictionary for which function to call when handling which event
event_handler_dictionary = {
    "arrival"           : arrival,
    "finished charging" : finished_charging,
    "leave parking"     : leave_parking
}

def event_handler(event, eventQ, parking, cables, network, csv, statistics):
    event_handler_dictionary[event.type](event,
                                         eventQ,
                                         parking,
                                         cables,
                                         network,
                                         csv
                                        ) #call the propert function according to the event type and the dictionary
    update_statistics(event.time, statistics, parking, cables)
