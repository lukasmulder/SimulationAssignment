from queue import PriorityQueue


class Car:
    def __init__(self, time, volume, connection_time, loc, status):
        self.arrival_time = time
        self.volume = volume # charging volume
        self.connection_time = connection_time
        self.loc = loc
        self.status = status # Either "parked", "charging", "finished"

class Parking:
    def __init__(self, id, capacity, parent_cable, choice, queue = PriorityQueue(), charging = 0):
        self.id = id #the number of the parking lot
        self.capacity = capacity
        self.parent_cable_id = parent_cable # parent cable it is connected to
        self.choice = choice #first choice parking percentage
        self.cars = [] #array of parked cars
        self.charging = charging #number of charging cars in parking
        self.queue = queue

class Cable:
    def __init__(self, id, capacity, parent):
        self.id = id #the number of the cable
        self.capacity = capacity #its maximum capacity
        self.flow = 0 #its current flow
        self.parent_cable_id = parent
        self.solar = 0 # amount of solar energy genereated at the parking lot at the end of the cable.
                       # relevant for cables 1, 2, 5, 8 (parking lots 1, 2, 7, and 6 respectively)

class State:
    def __init__(self):

        self.cables =    { 0 : Cable(0, 200, 9) #initializing all the cables with their correct values
                         , 1 : Cable(1, 200, 0)
                         , 2 : Cable(2, 200, 0)
                         , 3 : Cable(3, 200, 0)
                         , 4 : Cable(4, 200, 9)
                         , 5 : Cable(5, 200, 4)
                         , 6 : Cable(6, 200, 4)
                         , 7 : Cable(7, 200, 6)
                         , 8 : Cable(8, 200, 6)
                         , 9 : Cable(9, 1000, None) #cable to the transformer
                         }
        self.parking =    { 1 : Parking(1, 60, 1, 0.15) #initializing all the parking lots with the correct values
                          , 2 : Parking(2, 80, 2, 0.15)
                          , 3 : Parking(3, 60, 3, 0.15)
                          , 4 : Parking(4, 70, 4, 0.20)
                          , 5 : Parking(5, 60, 7, 0.15)
                          , 6 : Parking(6, 60, 8, 0.10)
                          , 7 : Parking(7, 50, 5, 0.10)
                          }
        self.global_queue = PriorityQueue()

# If a demand change at a parking occurs, update_flow(parking, flow_change)
# changes the flow through the network
# Positive flow indicates flow from the transformer to the parking (demand)
# negative flow indicates flow from the parking to the transformer (solar supply)
def update_flow(cables, parking, flow_change):
    parent_cable_id = parking.parent_cable_id
    _update_flow(cables, parent_cable_id, flow_change)

# helper function for updating flow
def _update_flow(cables, cable_id, flow_change):
    cable = cables[cable_id]
    cable.flow += flow_change
    if cable.parent_cable_id != None:
        _update_flow(cables, cable.parent_cable_id, flow_change)



def print_state(state):
    print("Parking (id, free, charging)")
    for id, loc in state.parking.items():

        free = loc.capacity - len(loc.cars)
        charging = len(list(filter( lambda x: x.status == "charging", loc.cars)))

        print(loc.id, free, charging)
    print()
    print("Cables (id, capacity, flow)")
    for id, cable in state.cables.items():
        print(cable.id, cable.capacity, cable.flow)
    print("---------------------------------------")
