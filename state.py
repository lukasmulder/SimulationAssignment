from queue import PriorityQueue

class Car:
    def __init__(self, time, volume, connection_time, loc, status):
        self.arrival_time = time
        self.volume = volume # charging volume
        self.connection_time = connection_time
        self.loc = loc
        self.status = status # Either "parked", "charging", "finished"

class Parking:
    def __init__(self, id, capacity, parent_cable, choice, queue = PriorityQueue(), charging = 0, solar = False):
        self.id = id #the number of the parking lot
        self.capacity = capacity
        self.solar = solar
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

    def print_state(self):
        print("Parking (id, #cars, free, charging)")
        for id, loc in self.parking.items():

            free = loc.capacity - len(loc.cars)
            charging = len(list(filter( lambda x: x.status == "charging", loc.cars)))

            print(loc.id, len(loc.cars), free, charging)
        print()
        print("Cables (id, capacity, flow)")
        for id, cable in self.cables.items():
            print(cable.id, cable.capacity, cable.flow)
        print("---------------------------------------")

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

# helper function for updating model after a change in solar output
def update_solar(cables, parking, new_flow, current_flow):
    solar_parking = list(filter(lambda x : parking[x].solar, parking)) # array of keys of all solar parking
    for loc in solar_parking:
        update_flow(cables, parking[loc], current_flow - new_flow)

#function that returns id of all parents cables of a parking
def find_parents(cables, parking):
    parents = [parking.parent_cable_id]
    return _find_parents(cables,parents)

#helper function for find_parents
def _find_parents(cables, parents):
    cable = cables[parents[-1]]
    if cable.parent_cable_id != None:
        parents.append(cable.parent_cable_id)
        return _find_parents(cables,parents)
    else:
        return parents
