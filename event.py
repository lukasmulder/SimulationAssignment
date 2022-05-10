from state      import State
from statistics import Statistics, update_load_statistics
from helper     import *

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


def arrival(event, eventQ, parking, cables, network, csv, statistics):
    currenttime = event.time
    parkingchoices = chooseparking()
    for loc in parkingchoices:
        if parking[loc].free > 0:
            #park car
            parking[loc].free-=1

            #charge car
            parking[loc].charging+=1

            #update cables
            for cable in network[loc]:
                cable.flow += 6

            ch,le = generate_time(csv)
            #schedule finished charging
            chargetime = currenttime + ch

            insert_event(Event(chargetime,"finished charging",loc),eventQ)

            #schedule leave parking
            leavetime = currenttime + le
            insert_event(Event(leavetime,"leave parking",loc),eventQ)

            break

        statistics.non_served_vehicles += 1

    statistics.total_vehicles += 1

    next_arrival_time = generate_arrival_time(currenttime, csv)
    insert_event(Event(next_arrival_time, "arrival"), eventQ)


def finished_charging(event, eventQ, parking, cables, network, csv, statistics):
    loc = event.location #get the location where the car is parked
    parking[loc].charging -= 1
    for cable in network[loc]: #for every cable in the network that transports current to the car
        cable.flow -= 6 #reduce the flow by 6 kWh

def leave_parking(event, eventQ, parking, cables, network, csv, statistics):
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
                                         csv,
                                         statistics
                                        ) #call the propert function according to the event type and the dictionary
    update_load_statistics(event.time, statistics, cables)
