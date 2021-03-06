import time
import random
from state import State, find_parents
from event import Event, print_eventQ, event_handler, import_from_csv
from solar import Solar
from statistics import *
from output import *
from plotting import *
from queue import PriorityQueue

#init takes a list of all parking spots with a solar panel and returns all the relevant initials
def init(solar_locations):
    eventQ = [Event(0, "solar change", flow = 0), Event(0, "arrival")]

    state = State()
    for loc in solar_locations:
        state.parking[loc].solar = True

    solar = Solar()

    csv = {"arrival": import_from_csv("arrival_hours.csv"),
           "charging": import_from_csv("charging_volume.csv"),
           "connection": import_from_csv("connection_time.csv")}


    return(eventQ, state, solar, csv)

#runs an event simulation using the parameters specfified.
def simulate(run_time, season, solar_locations, fname, strategy, verbose = False):
    #initialition
    eventQ, state, solar, csv = init(solar_locations)

    day = 0
    all_statistics = []
    statistics = Statistics(day)

    #main loop
    while eventQ != [] and eventQ[0].time < run_time: #check if the queuue is not empty and if we have not exceeded the simulation time.

        if eventQ[0].time > (day + 1) * 60 * 24:
            all_statistics.append(statistics) # save the current statistics
            day += 1 # increment the day
            statistics = Statistics(day) # create a fresh one

        #handle event
        event_handler(eventQ.pop(0),
                      eventQ,
                      state.parking,
                      state.cables,
                      state.global_queue,
                      solar,
                      season,
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
            eventQ[0].print_event()
            print("---------------------")
            state.print_state()

    all_statistics.append(statistics)

    return all_statistics


#runs the simulation for all combinations of strategies, seasons and solar panels, and computes the relevant output statitsics.
def main(warm_up, run_time, confidence, standard_summer, standard_winter, standard_strat_3, standard_strat_4):

    solar_locations = [[],[6,7], [1,2,6,7]]
    strategies = [1,2,3,4]
    seasons = ["summer", "winter"]

    t0 = time.time()

    prepare_save_files(run_time, warm_up)

    all_statistics = {}

    for strategy in strategies:
        for solar_location in solar_locations:
            if solar_location != []:
                s_statistics = simulate(run_time, "summer", solar_location, "", strategy, verbose = False)
                w_statistics = simulate(run_time, "winter", solar_location, "", strategy, verbose = False)
                all_statistics["{}{}summer".format(solar_location, strategy)] = s_statistics[warm_up:]
                all_statistics["{}{}winter".format(solar_location, strategy)] = w_statistics[warm_up:]
                save_data(run_time, warm_up, s_statistics, w_statistics, solar_location, strategy)

            else:
                statistics = simulate(run_time, "summer", solar_location, "", strategy, verbose = False) #season doesnt matter if there are no solar panels
                save_data(run_time, warm_up, statistics, statistics, solar_location, strategy)
                all_statistics["{}{}summer".format(solar_location, strategy)] = statistics[warm_up:]
                all_statistics["{}{}winter".format(solar_location, strategy)] = statistics[warm_up:]
                if strategy == 1:
                    plot_load_over_time(merge_statistics(statistics[:7]), solar_location, "load_over_time") #plot one figure to show the warm_up of two days is okay.


    compute_statistics(all_statistics,
                       standard_summer,
                       standard_winter,
                       (standard_strat_3, all_statistics[standard_strat_3]),
                       (standard_strat_4, all_statistics[standard_strat_4]),
                       confidence)

    for name, statistics in all_statistics.items():
        # plot the cable loads for the last 3 days for all simulations.
        plot_all_cable_loads(merge_statistics(statistics[-3:]),  "All_cable_loads_{}".format(name))

    close_save_files()

    t1 = time.time()
    print("total time: {} seconds".format(t1-t0))


warm_up = 2 # number of days of warm_up
run_time = 24*60*warm_up + 60*24*60
confidence = 0.95

standard_summer = "{}{}summer".format([1,2,6,7], 4)
standard_winter = "{}{}winter".format([1,2,6,7], 4)
standard_strat_3 = "{}{}summer".format([], 3)
standard_strat_4 = "{}{}summer".format([], 4)

main(warm_up, run_time, confidence, standard_summer, standard_winter, standard_strat_3, standard_strat_4)
