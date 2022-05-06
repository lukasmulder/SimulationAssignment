class Parking:
    def __init__(self, id, free, choice):
        self.id = id #the number of the parking lot
        self.free = free #amount of available spaces
        self.charging = 0 #amount of vehicles charging
        self.choice = choice #first choice parking percentage

parking = { 1 : Parking(1, 60, 0.15) #initializing all the parking lots with the correct values
          , 2 : Parking(2, 80, 0.15)
          , 3 : Parking(3, 60, 0.15)
          , 4 : Parking(4, 70, 0.20)
          , 5 : Parking(5, 60, 0.15)
          , 6 : Parking(6, 60, 0.10)
          , 7 : Parking(7, 50, 0.10)
          }

class Cable:
    def __init__(self, id, capacity):
        self.id = id #the number of the cable
        self.capacity = capacity #its maximum capacity
        self.flow = 0 #its current flow

cables = { 0 : Cable(0, 200) #initializing all the cables with their correct values
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


#the network of cables and parking lots
#the keys are the parking lots, the list contains all the cables current runs through. 
network =  { 1 : [cables[0], cables[1], cables[9]]
           , 2 : [cables[0], cables[2], cables[9]]
           , 3 : [cables[0], cables[3], cables[9]]
           , 4 : [cables[4], cables[9]]
           , 5 : [cables[4], cables[6], cables[7], cables[9]]
           , 6 : [cables[4], cables[6], cables[8], cables[9]]
           , 7 : [cables[4], cables[5], cables[9]]
           }
