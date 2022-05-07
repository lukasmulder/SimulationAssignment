from state import State
from event import *

"""
TODO:
- event handler
    -write generator for times (charging, leaving, arrival)
- implement statistics
- make use of Poisson distribution
"""

def main(run_time):
    #initialition
    eventQ = [Event(0, "arrival")]
    state = State()
    csv = {"arrival": import_from_csv("arrival_hours.csv"),
           "charging": import_from_csv("charging_volume.csv"),
           "connection": import_from_csv("connection_time.csv")}
    

    #main loop
    while eventQ != [] and eventQ[0].time < run_time: #check if the queuue is not empty and if we have not exceeded the simulation time.
        # print("\n\neventQ")
        # for event in eventQ:
        #     print(event.type, event.time)
        print(eventQ[0].type,eventQ[0].time)
        
        event_handler(eventQ.pop(0), eventQ, state.parking, state.cables, state.network, csv)

main(24*60)
