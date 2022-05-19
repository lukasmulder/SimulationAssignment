import time
from state import State, print_state
from event import Event, print_event, print_eventQ, event_handler, import_from_csv
from statistics import Statistics, update_load_statistics, update_parking_statistics, generate_report
from queue import PriorityQueue


def init():
    eventQ = [Event(0, "arrival")]
    state = State()
    csv = {"arrival": import_from_csv("arrival_hours.csv"),
           "charging": import_from_csv("charging_volume.csv"),
           "connection": import_from_csv("connection_time.csv")}
    statistics = Statistics()
    return(eventQ, state, csv, statistics)

def main(run_time, strategy = None, verbose = False):
    #initialition
    eventQ, state, csv, statistics = init()

    #main loop
    while eventQ != [] and eventQ[0].time < run_time: #check if the queuue is not empty and if we have not exceeded the simulation time.
        #handle event
        event_handler(eventQ.pop(0),
                      eventQ,
                      state.parking,
                      state.cables,
                      state.network,
                      csv,
                      statistics,
                      strategy
                     )

        #update statistics
        update_load_statistics(eventQ[0].time, statistics, state.cables)
        update_parking_statistics(statistics, state.parking)

        #print extra information if needed
        if verbose:
            print_eventQ(eventQ)
            print()
            print("Current event")
            print_event(eventQ[0])
            print_state(state)

    #generate final report
    generate_report(run_time, state, statistics)

t0 = time.time()
strategy = 3 #can be 1-4
main(60*24*2, strategy, verbose = False)
t1 = time.time()

print("total time: {} seconds".format(t1-t0))
