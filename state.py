from queue import PriorityQueue


class Car:
    def __init__(self, time, volume, connection_time, loc, status):
        self.arrival_time = time
        self.volume = volume #charging volume
        self.connection_time = connection_time
        self.loc = loc
        self.status = status #Either "parked", "charging", "finished"

class Parking:
    def __init__(self, id, capacity, choice, queue = PriorityQueue(), charging =0):
        self.id = id #the number of the parking lot
        self.capacity = capacity
        self.choice = choice #first choice parking percentage
        self.cars = [] #array of parked cars
        self.charging = charging #number of charging cars in parking
        self.queue = queue

class Cable:
    def __init__(self, id, capacity):
        self.id = id #the number of the cable
        self.capacity = capacity #its maximum capacity
        self.flow = 0 #its current flow

class State:
    def __init__(self):
        self.parking =    { 1 : Parking(1, 60, 0.15) #initializing all the parking lots with the correct values
                          , 2 : Parking(2, 80, 0.15)
                          , 3 : Parking(3, 60, 0.15)
                          , 4 : Parking(4, 70, 0.20)
                          , 5 : Parking(5, 60, 0.15)
                          , 6 : Parking(6, 60, 0.10)
                          , 7 : Parking(7, 50, 0.10)
                          }

        #is dit niet onnodig extra? de cables zitten al ingebouwd in het network
        self.cables =    { 0 : Cable(0, 200) #initializing all the cables with their correct values
                         , 1 : Cable(1, 200)
                         , 2 : Cable(2, 200)
                         , 3 : Cable(3, 200)
                         , 4 : Cable(4, 200)
                         , 5 : Cable(5, 200)
                         , 6 : Cable(6, 200)
                         , 7 : Cable(7, 200)
                         , 8 : Cable(8, 200)
                         , 9 : Cable(9, 1000) #cable to the transformer
                         }

        self.network = { 1 : [self.cables[0], self.cables[1], self.cables[9]]
                       , 2 : [self.cables[0], self.cables[2], self.cables[9]]
                       , 3 : [self.cables[0], self.cables[3], self.cables[9]]
                       , 4 : [self.cables[4], self.cables[9]]
                       , 5 : [self.cables[4], self.cables[6], self.cables[7], self.cables[9]]
                       , 6 : [self.cables[4], self.cables[6], self.cables[8], self.cables[9]]
                       , 7 : [self.cables[4], self.cables[5], self.cables[9]]
                   }

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
