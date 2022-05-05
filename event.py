class Event:
    def __init__(self, time, type):
        self.time = time
        self.type = type #"arrival", "finished charging", of "leave parking"
        self.location = None

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


def arrival(event, eventQ, parking, cables, network):
    #check which parking lots are have empty spaces
    #for all parking lots with empty spaces, choose one according to their weights
    #increase the current flow through the relevant cables
    #schedule finished_charging
    #schedule leave_parking

def finished_charging(event, eventQ, parking, cables, network):
    loc = event.location #get the location where the car is parked
    for cable in network[loc]: #for every cable in the network that transports current to the car
        cable.flow -= 6 #reduce the flow by 6 kWh

def leave_parking(event, eventQ, parking, cables, network):
    loc = event.location #get the location where the care was parked
    parking[loc - 1].free += 1 #free up one space from the parking lot

#dictionary for which function to call when handling which event
event_handler_dictionary = {
    "arrival"           : arrival,
    "finished charging" : finished_charging,
    "leave parking"     : leave_parking
}

def event_handler(event, eventQ, parking, cables, network):
    event_handler_dictionary[event.type](event, eventQ, parking, cables, network) #call the propert function according to the event type and the dictionary
