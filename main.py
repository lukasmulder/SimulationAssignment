from state import State, print_state
from event import Event, event_handler, import_from_csv
from statistics import *


def init():
    eventQ = [Event(0, "arrival")]
    state = State()
    csv = {"arrival": import_from_csv("arrival_hours.csv"),
           "charging": import_from_csv("charging_volume.csv"),
           "connection": import_from_csv("connection_time.csv")}
    statistics = Statistics()
    return(eventQ, state, csv, statistics)

def main(run_time):
    #initialition
    eventQ, state, csv, statistics = init()

    #main loop
    while eventQ != [] and eventQ[0].time < run_time: #check if the queuue is not empty and if we have not exceeded the simulation time.
        event_handler(eventQ.pop(0),
                      eventQ,
                      state.parking,
                      state.cables,
                      state.network,
                      csv,
                      statistics
                     )
        # print("\n\neventQ")
        # for event in eventQ:
        #     print(event.type, event.time)
        # print()
        #print(eventQ[0].type,eventQ[0].time)
        #print_state(state)

    generate_report(run_time, statistics)


main(60*25)
