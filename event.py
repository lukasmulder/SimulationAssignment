
from numpy.random import choice
from state import *
import random
import math
import csv
import pandas as pd
from pandas import *

class Event:
    def __init__(self, time, type,location=None):
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


def arrival(event, eventQ, parking, cables, network, arrivalrates):
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

            ch,le = generate_time()
            #schedule finished charging
            chargetime = currenttime + ch
            
            insert_event(Event(chargetime,"finished charging",n),eventQ)

            #schedule leave parking
            leavetime = currenttime + le
            insert_event(Event(leavetime,"leave parking",n),eventQ)
            
            break

    next_arrival_time = generate_arrival_time(currenttime, arrivalrates)
    insert_event(Event(next_arrival_time, "arrival"), eventQ)

def generate_arrival_time(currenttime,arrivalrates):
    rate = (750*arrivalrates[int(currenttime/60)])/60 # this function should give the average number of cars in that hour
    p = random.random()
    arrival_time= -math.log(1 - p)/rate
    return currenttime + arrival_time

def import_from_csv(filename):
    #extracts second column from csv file and returns a list of floats
    data = read_csv(filename, sep = ";")
    
    info = data['Share of charging transactions'].tolist()
        
    return list(map(float, info))

def generate_time():
    #generates charging time and leaving time
    a=2
    b=4
    return (a,b)

def chooseparking():
    #generates 3 parking spaces that will be picked radnomly
    #parking spaces can be the same vgm willen wij dat niet
    return choice([1,2,3,4,5,6,7], size = 3, replace = False, p=[0.15,0.15,0.15,0.2,0.15,0.1,0.1])

def finished_charging(event, eventQ, parking, cables, network,arrivalrates):
    loc = event.location #get the location where the car is parked
    for cable in network[loc]: #for every cable in the network that transports current to the car
        cable.flow -= 6 #reduce the flow by 6 kWh

def leave_parking(event, eventQ, parking, cables, network,arrivalrates):
    loc = event.location #get the location where the care was parked
    parking[loc].free += 1 #free up one space from the parking lot

#dictionary for which function to call when handling which event
event_handler_dictionary = {
    "arrival"           : arrival,
    "finished charging" : finished_charging,
    "leave parking"     : leave_parking
}

def event_handler(event, eventQ, parking, cables, network,arrivalrates):
    event_handler_dictionary[event.type](event, eventQ, parking, cables, network, arrivalrates) #call the propert function according to the event type and the dictionary

print(import_from_csv("charging_volume.csv"))