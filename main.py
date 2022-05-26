import time
from state import State, print_state, find_parents
from event import Event, print_event, print_eventQ, event_handler, import_from_csv
from solar import Solar
from statistics import *
from output import calculate_average_measures, save_measures, merge_statistics
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

def main(run_time, season, solar_locations, fname, strategy, verbose = False):
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
            # print_eventQ(eventQ)
            # print()
            # print("Current event")
            # print_event(eventQ[0])
            # print("---------------------")
            print_state(state)

    all_statistics.append(statistics)

    #generate final data

    # for i in range(len(all_statistics)):
        #generate_report(run_time/(day+1), state, all_statistics[i], season, solar_locations, strategy, fname + str(i))
        #save_data(run_time, state, all_statistics[i], season, solar_locations, strategy, fname + str(i))
        #dump_load_over_time(all_statistics[i])
        #plot_load_over_time(all_statistics[i])
        #plot_solar_over_time(all_statistics[i], solar_locations)
        #plot_solar_percentage_over_time(all_statistics[i], solar_locations)

    #calculate_average_measures(all_statistics, run_time, warm_up, solar_locations)
    #save_measures(all_statistics, run_time, warm_up, solar_locations, fname)

    return all_statistics

solar_locations = [[],[1,2], [1,2,6,7]]
strategies = [1,2,3,4]
seasons = ["summer", "winter"]
warm_up = 2 # number of days of warm_up
run_time = 24*60*warm_up + 60*24*60

t0 = time.time()

f = open("./results/results.csv", "w")
f.write("run time: {}; warm up: {}\n".format(run_time, warm_up))
f.write("average_delay; average_revenue; average_solar_revenue; average_overload_percentage; strategy\n")

for solar_location in solar_locations:
    for strategy in strategies:
        if solar_location != []:
            for season in seasons:
                all_statistics = main(run_time, season, solar_location, "./results/{} {} {}".format(solar_location, season, strategy), strategy, verbose = False)
                measures = calculate_average_measures(all_statistics, run_time, warm_up, solar_location)
                f.write("{}; {}; {}; {}; ".format(*measures))
                f.write("{} {} {}\n".format(solar_location, season, strategy))
                plot_load_over_time(merge_statistics(all_statistics), solar_location, "{} {} {}".format(solar_location, season, strategy))
        else:
            all_statistics = main(run_time, "winter", solar_location, "./results/base {}".format(strategy), strategy, verbose = False) #season doesnt matter if there are no solar panels
            measures = calculate_average_measures(all_statistics, run_time, warm_up, solar_location)
            f.write("{}; {}; {}; {}; ".format(*measures))
            f.write("base {}\n".format(strategy))
            plot_load_over_time(merge_statistics(all_statistics), solar_location, "base {}".format(strategy))

# all_statistics = main(run_time, "winter", solar_locations[0], "./results/test", strategies[3], verbose = True)
# statistic = merge_statistics(all_statistics)
# measures = calculate_average_measures(all_statistics, run_time, warm_up, solar_locations[0])
# f.write("{}; {}; {}; {}; ".format(*measures))

t1 = time.time()
f.write("total time: {} seconds".format(t1-t0))
f.close()
