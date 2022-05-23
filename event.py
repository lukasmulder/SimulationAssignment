from state      import State, Car, update_flow, update_solar
from statistics import Statistics, update_load_statistics, update_delay_statistics
from helper     import *
from queue import PriorityQueue

class Event:
    def __init__(self, time, type, loc = None, car = None, flow = None):
        self.time = time
        self.type = type #"arrival", "finished charging", of "departure"
        self.loc = loc
        self.car = car
        self.flow = flow

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

def arrival(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
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

def parking(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    #get all relevant variables
    current_time = event.time
    loc = event.loc

    #calculate relevant new variables
    charging_volume, connection_time, delay = generate_time(csv)
    car = Car(current_time, charging_volume, connection_time, loc=loc, status = "parked")

    update_delay_statistics(statistics, delay)

    #update the model
    parking[loc].cars.append(car)

    #insert new event
    if strategy == 1: #base strategy

        event = Event(current_time, "start charging", loc = loc, car = car)
        insert_event(event, eventQ)

    elif strategy == 2: #price reduction strategy

        event = Event(price_reduc_time(current_time,charging_volume,connection_time), "start charging", loc = loc, car = car)
        insert_event(event, eventQ)

    else:

        if check_charging_possibility(cables, parking[loc], 6): #check we can charge here
            event = Event(current_time, "start charging", loc = loc, car = car)
            insert_event(event, eventQ)
        else:
            queue = parking[loc].queue
            #put car in queues
            if strategy == 3 :
                queue.put((current_time, car))
                global_queue.put((current_time, car))
            elif strategy == 4 :
                charging_time = (charging_volume / 6) * 60
                latest_start_time = current_time + connection_time - charging_time
                queue.put((latest_start_time,car))
                global_queue.put((latest_start_time,car))






def start_charging(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
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

def stop_charging(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    #get all relevant variables
    current_time = event.time
    car = event.car
    loc = event.loc

    #update the state
    car.status = "parked" #for the base case we know it is now full, need to keep track of a battery meter in the future
    parking[loc].charging -= 1
    update_flow(cables, parking[loc], -6)

    #insert new event
    event = Event(current_time, "finished charging", loc = loc, car = car) # this still assumes a vehicle charging is never interrupted
    insert_event(event, eventQ)

    #schedule start charging for next car in queue
    if strategy == 3 or strategy == 4:
        #queue = parking[loc].queue
        if not global_queue.empty():
            time, next_car = global_queue.get() # check which car in the global queue is next
            next_loc = next_car.loc

            if check_charging_possibility(cables, parking[next_loc], 6): #check we can charge the next car in the queue
                #get car from local queue
                parking[next_loc].queue.get()

                #schedule start charging of first car from queue
                event = Event(current_time, "start charging", loc = next_loc, car = next_car)
                insert_event(event, eventQ)
            else:
                #reinsert
                global_queue.put((time,next_car))


def finished_charging(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    #get all relevant variables
    current_time = event.time
    loc = event.loc
    car = event.car

    #update the state
    car.status = "finished"

    #insert new event
    event = Event(current_time, "departure", loc = loc, car = car)
    insert_event(event, eventQ)

def departure(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    loc = event.loc #get the loc where the car is parked
    car = event.car
    parking[loc].cars.remove(car)

def price_change(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    pass

def solar_change(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    current_time = event.time
    current_flow = event.flow
    factor = solar.generate(season, current_time // 60)
    # needs to update all parking spots with solar
    # needs to be aware of preveous solar output
    update_solar(cables, parking, factor * 200, current_flow)

    event = Event(current_time + 60, "solar change", flow = factor * 200)
    insert_event(event, eventQ)



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

def event_handler(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    event_handler_dictionary[event.type](event,
                                         eventQ,
                                         parking,
                                         cables,
                                         global_queue,
                                         solar,
                                         season,
                                         csv,
                                         statistics,
                                         strategy
                                        ) #call the propert function according to the event type and the dictionary
