
from numpy.random import choice

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


def arrival(event, eventQ, parking, cables, network):
    currenttime = event.time
    parkingchoices = chooseparking()
    for n in parkingchoices:
        if parking[n].free > 0:
            #park car
            parking[n].free-=1

            #charge car
            parking[n].charging+=1
            #update cables
            updatecables(network,n)

            #schedule finished charging
            chargetime = currenttime + generate_time()[0]
            insert_event(Event(chargetime,"finished charging",n),eventQ)

            #schedule leave parking
            leavetime = currenttime + generate_time()[1]
            insert_event(Event(leavetime,"leave parking",n),eventQ)

            break

    next_arrival_time = currenttime + 1
    insert_event(Event(next_arrival_time, "arrival"), eventQ)

def updatecables(network,parking):
    for cable in network[parking]:
        cable.flow += 6


def generate_time():
    #generates charging time and leaving time
    a=1
    b=10
    return (a,b)

def chooseparking():
    #generates 3 parking spaces that will be picked radnomly
    #parking spaces can be the same vgm willen wij dat niet
    return choice([1,2,3,4,5,6,7], size = 3, replace = False, p=[0.15,0.15,0.15,0.2,0.15,0.1,0.1])

def finished_charging(event, eventQ, parking, cables, network):
    loc = event.location #get the location where the car is parked
    for cable in network[loc]: #for every cable in the network that transports current to the car
        cable.flow -= 6 #reduce the flow by 6 kWh

def leave_parking(event, eventQ, parking, cables, network):
    loc = event.location #get the location where the care was parked
    parking[loc].free += 1 #free up one space from the parking lot

#dictionary for which function to call when handling which event
event_handler_dictionary = {
    "arrival"           : arrival,
    "finished charging" : finished_charging,
    "leave parking"     : leave_parking
}

def event_handler(event, eventQ, parking, cables, network):
    event_handler_dictionary[event.type](event, eventQ, parking, cables, network) #call the propert function according to the event type and the dictionary
