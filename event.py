from state      import State, Car, update_flow, update_solar
from statistics import Statistics, update_load_statistics, update_delay_statistics, update_solar_statistics
from helper     import *
from queue import PriorityQueue

class Event:
    def __init__(self, time, type, loc = None, car = None, flow = None):
        self.time = time
        self.type = type #"arrival", "finished charging", of "departure"
        self.loc = loc
        self.car = car
        self.flow = flow

    def print_event(self):
        print(self.type, self.time)

#prints the entire eventqueue
def print_eventQ(eventQ):
    for event in eventQ:
        print_event(event)

# Insert event in eventQ, and keep it sorted assuming it is sorted.
# If event an event has the same time as an event already in the eventQ,
# insert it to the right of the rightmost event.
def insert_event(event, eventQ):
    low = 0
    high = len(eventQ)

    while low < high:
        mid = (low+high)//2
        if event.time < eventQ[mid].time:
            high = mid
        else:
            low = mid+1
    eventQ.insert(low, event)

# event handler for arrival
def arrival(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    # get relevant variables
    current_time = event.time
    parkingchoices = chooseparking()

    # try and find a free parking space
    for loc in parkingchoices:
        if parking[loc].capacity > len(parking[loc].cars):
            #if a parking lot is free, create the parking event
            event = Event(current_time, "parking", loc = loc)
            insert_event(event, eventQ)

            statistics.non_served_vehicles -= 1

            break

    #updat statistics
    statistics.total_vehicles += 1
    statistics.non_served_vehicles += 1 # assume we can not serve the vehicle and then decrement it when we do serve it

    # schedulde next event
    next_arrival_time = generate_arrival_time(current_time, csv)
    insert_event(Event(next_arrival_time, "arrival"), eventQ)

# event handler for parking
def parking(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    #get all relevant variables
    current_time = event.time
    loc = event.loc

    #calculate relevant new variables
    charging_volume, connection_time = generate_time(csv)
    car = Car(current_time, charging_volume, connection_time, loc=loc, status = "parked")

    #update the model
    parking[loc].cars.append(car)

    # insert new event
    # the way this is done depends on the strategy
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
                charging_time = charging_volume *10
                latest_start_time = current_time + connection_time - charging_time
                queue.put((latest_start_time,car))
                global_queue.put((latest_start_time,car))

# event handler for start charging
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

# event handler for stop charging
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

    #schedule start charging for next car in queue, if this is necessary due to the strategy
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

# event handler for finished charging
def finished_charging(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    #get all relevant variables
    current_time = event.time
    loc = event.loc
    car = event.car

    #update the state
    car.status = "finished"

    #insert new event
    departure_time = max(current_time, car.arrival_time+car.connection_time)
    event = Event(departure_time, "departure", loc = loc, car = car)
    insert_event(event, eventQ)

# event handler for deparure
def departure(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    current_time = event.time
    loc = event.loc
    car = event.car

    update_delay_statistics(statistics, current_time, car)

    parking[loc].cars.remove(car)

# event handler for solar change
def solar_change(event, eventQ, parking, cables, global_queue, solar, season, csv, statistics, strategy):
    current_time = event.time
    current_flow = event.flow
    factor = solar.generate(season, current_time // 60)
    # needs to update all parking spots with solar
    # needs to be aware of preveous solar output
    update_solar(cables, parking, factor * 200, current_flow)
    update_solar_statistics(current_time, statistics, factor)

    # schedule start charging for next car in queue if possible
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
    "solar change"      : solar_change
}

# selects the correct event handler depending on the type of the event given.
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
