from state import State
from event import event_handler, Event, import_arrival_rates

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
    arrival_rates = import_arrival_rates()

    #main loop
    while eventQ != [] and eventQ[0].time < run_time: #check if the queuue is not empty and if we have not exceeded the simulation time.
        print("\n\neventQ")
        for event in eventQ:
            print(event.type, event.time)
        event_handler(eventQ.pop(0), eventQ, state.parking, state.cables, state.network, arrival_rates)

main(24*60)
