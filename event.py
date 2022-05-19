from state      import State, Car, update_flow
from statistics import Statistics, update_load_statistics
from helper     import *
from queue import PriorityQueue

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

def arrival(event, eventQ, parking, cables, csv, statistics, strategy):
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

def parking(event, eventQ, parking, cables, csv, statistics, strategy):
    #get all relevant variables
    current_time = event.time
    loc = event.loc

    #calculate relevenent new variables
    charging_volume, connection_time = generate_time(csv)
    car = Car(current_time, charging_volume, connection_time, loc, "parked")

    #update the model
    parking[loc].cars.append(car)

    #insert new event
    if strategy ==1: #base strategy

        event = Event(current_time, "start charging", loc = loc, car = car)
        insert_event(event, eventQ)
    elif strategy == 2: #price reduction strategy

        event = Event(price_reduc_time(current_time,charging_volume,connection_time), "start charging", loc = loc, car = car)
        insert_event(event, eventQ)
    else:

        queue = parking[loc].queue
        if parking[loc].charging < max_num_charging(loc): #check if the max number of cars is charging
            event = Event(current_time, "start charging", loc = loc, car = car)
            insert_event(event, eventQ)
        else: #put car in queue
            if strategy==3 :
                queue.put((current_time,car))
            elif strategy ==4 :
                charging_time = (charging_volume / 6) * 60
                latest_start_time = current_time +connection_time - charging_time
                queue.put((latest_start_time,car))


def start_charging(event, eventQ, parking, cables, csv, statistics, strategy):
    #get all relevant variables
    current_time = event.time
    car = event.car
    loc = event.loc

    #calculate relevenent new variables
    stop_time = current_time + (car.volume / 6) * 60

    #update the model
    car.status = "charging"
    parking[loc].charging +=1
    update_flow(cables, parking[loc], 6)

    #insert new event
    insert_event(Event(stop_time, "stop charging", loc = loc, car = car), eventQ)

def stop_charging(event, eventQ, parking, cables, csv, statistics, strategy):
    #get all relevant variables
    current_time = event.time
    car = event.car
    loc = event.loc

    #update the state
    car.status = "parked" #for the base case we know it is now full, need to keep track of a battery meter in the future
    parking[loc].charging -=1
    update_flow(cables, parking[loc], -6)

    #insert new event
    event = Event(current_time, "finished charging", loc = loc, car = car)
    insert_event(event, eventQ)

    #schedule start charging for next car in queue
    if strategy == 3 or strategy == 4:
        queue = parking[loc].queue
        nextcar = queue.get()[1]
        event = event = Event(current_time, "start charging", loc = loc, car = nextcar)
        insert_event(event, eventQ)


def finished_charging(event, eventQ, parking, cables, csv, statistics, strategy):
    #get all relevant variables
    current_time = event.time
    loc = event.loc
    car = event.car

    #update the state
    car.status = "finished"

    #insert new event
    event = Event(current_time, "departure", loc = loc, car = car)
    insert_event(event, eventQ)

def departure(event, eventQ, parking, cables, csv, statistics, strategy):
    loc = event.loc #get the loc where the car is parked
    car = event.car
    parking[loc].cars.remove(car)

def price_change(event, eventQ, parking, cables, csv, statistics, strategy):
    pass

def solar_change(event, eventQ, parking, cables, csv, statistics, strategy):
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

def event_handler(event, eventQ, parking, cables, csv, statistics,strategy):
    event_handler_dictionary[event.type](event,
                                         eventQ,
                                         parking,
                                         cables,
                                         csv,
                                         statistics,
                                         strategy
                                        ) #call the propert function according to the event type and the dictionary
