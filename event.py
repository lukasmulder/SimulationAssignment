from state      import State, Car
from statistics import Statistics, update_load_statistics
from helper     import *

class Event:
    def __init__(self, time, type, loc = None, car = None):
        self.time = time
        self.type = type #"arrival", "finished charging", of "departure"
        self.loc = loc
        self.car = car

def print_event(event):
    print(event.type, event.time)

def print_eventQ(eventQ):
    for event in eventQ:
        print_event(event)

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
    current_time = event.time
    parkingchoices = chooseparking()
    for loc in parkingchoices:
        if parking[loc].capacity > len(parking[loc].cars):
            #if a parking lot is free, create the parking event
            event = Event(current_time, "parking", loc = loc)
            insert_event(event, eventQ)

            break

        statistics.non_served_vehicles += 1

    statistics.total_vehicles += 1

    next_arrival_time = generate_arrival_time(current_time, csv)
    insert_event(Event(next_arrival_time, "arrival"), eventQ)

def parking(event, eventQ, parking, cables, network, csv, statistics):
    #get all relevant variables
    current_time = event.time
    loc = event.loc

    #calculate relevenent new variables
    charging_volume, connection_time = generate_time(csv)
    car = Car(current_time, charging_volume, connection_time, loc, "parked")

    #update the model
    parking[loc].cars.append(car)

    #insert new event
    event = Event(current_time, "start charging", loc = loc, car = car)
    insert_event(event, eventQ)

def start_charging(event, eventQ, parking, cables, network, csv, statistics):
    #get all relevant variables
    current_time = event.time
    car = event.car
    loc = event.loc

    #calculate relevenent new variables
    stop_time = current_time + (car.volume / 6) * 60

    #update the model
    car.status = "charging"
    for cable in network[loc]:
        cable.flow += 6

    #insert new event
    insert_event(Event(stop_time, "stop charging", loc = loc, car = car), eventQ)

def stop_charging(event, eventQ, parking, cables, network, csv, statistics):
    #get all relevant variables
    current_time = event.time
    car = event.car
    loc = event.loc

    #update the state
    car.status = "parked" #for the base case we know it is now full, need to keep track of a battery meter in the future
    for cable in network[loc]:
        cable.flow -= 6

    #insert new event
    event = Event(current_time, "finished charging", loc = loc, car = car)
    insert_event(event, eventQ)

def finished_charging(event, eventQ, parking, cables, network, csv, statistics):
    #get all relevant variables
    current_time = event.time
    loc = event.loc
    car = event.car

    #update the state
    car.status = "finished"

    #insert new event
    event = Event(current_time, "departure", loc = loc, car = car)
    insert_event(event, eventQ)

def departure(event, eventQ, parking, cables, network, csv, statistics):
    loc = event.loc #get the loc where the car is parked
    car = event.car
    parking[loc].cars.remove(car)

def price_change(event, eventQ, parking, cables, network, csv, statistics):
    pass

def solar_change(event, eventQ, parking, cables, network, csv, statistics):
    pass

#dictionary for which function to call when handling which event
event_handler_dictionary = {
    "arrival"           : arrival,
    "parking"           : parking,
    "start charging"    : start_charging,
    "stop charging"     : stop_charging,
    "finished charging" : finished_charging,
    "departure"         : departure,
    "price change"      : price_change,
    "solar change"      : solar_change
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
