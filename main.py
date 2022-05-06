from state import State
from event import event_handler, Event

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

    #main loop
    while eventQ != [] and eventQ[0].time < run_time: #check if the queuue is not empty and if we have not exceeded the simulation time.
        for event in eventQ:
            print(event.type, eventQ[0].time)
        event_handler(eventQ.pop(0), eventQ, state.parking, state.cables, state.network)

main(20)
