class Statistics:
    def __init__(self):
        self.load_over_time = { 0 : [(0,0)]
                              , 1 : [(0,0)]
                              , 2 : [(0,0)]
                              , 3 : [(0,0)]
                              , 4 : [(0,0)]
                              , 5 : [(0,0)]
                              , 6 : [(0,0)]
                              , 7 : [(0,0)]
                              , 8 : [(0,0)]
                              , 9 : [(0,0)]
                              }

        self.parked_vehicles_maximum =    { 1 : 0
                                          , 2 : 0
                                          , 3 : 0
                                          , 4 : 0
                                          , 5 : 0
                                          , 6 : 0
                                          , 7 : 0
                                          }

        self.non_served_vehicles = 0
        self.total_vehicles      = 0

        self.total_delay_time   = 0
        self.maximum_dalay_time = 0
        self.cars_with_delay    = 0

def update_parking_statistics(statistics, parking):
    for key, loc in parking.items():
        if statistics.parked_vehicles_maximum[key] < len(loc.cars):
            statistics.parked_vehicles_maximum[key] = len(loc.cars)

def update_load_statistics(current_time, statistics, cables):
    for loc, load_over_time in statistics.load_over_time.items():
        if (load_over_time[-1][1] != cables[loc].flow): #only append the array if the load over a cable changes
            load_over_time.append( (current_time, cables[loc].flow) )

def update_delay_statistics(statistics, delay):
    if delay > 0:
        statistics.total_delay_time += delay
        statistics.maximum_dalay_time = max(delay, statistics.maximum_dalay_time)
        statistics.cars_with_delay += 1

def generate_report(run_time, state, statistics):
    print("End of simulation, runtime was:", run_time)

    print("---------------------------------------------")

    for loc, parked_vehicles_maximum in statistics.parked_vehicles_maximum.items():
        print("parked vehicles maximum on parking {}: {}/{}".format(loc, parked_vehicles_maximum, state.parking[loc].capacity))

    print("---------------------------------------------")

    print("percentage of vehicles with a delay: {}%".format(100*statistics.cars_with_delay/statistics.total_vehicles))
    print("average delay over all vehicles: {} minutes".format(statistics.total_delay_time/statistics.total_vehicles))
    print("maximum delay: {} minutes".format(statistics.maximum_dalay_time))

    print("---------------------------------------------")

    for loc, load_over_time in statistics.load_over_time.items():
        print( "max load of cable", loc, max( [x[1] for x in load_over_time] ) )

    print("---------------------------------------------")

    #for loc, load_over_time in statistics.load_over_time.items():
    #    print( "load over time of cable", loc, load_over_time )

    for loc, load_over_time in statistics.load_over_time.items():
        cable_threshold = 200 if loc != 9 else 1000 #set cable cable_threshold according to which cable it is
        print( "overload of cable", loc, overload_in_cable(run_time, loc, load_over_time, cable_threshold) )

    print("overlad of network", overload_in_network(run_time, statistics))

    print("---------------------------------------------")

    print("total number of vehicles:", statistics.total_vehicles)
    print("fraction of non-served vehicles:", statistics.non_served_vehicles/statistics.total_vehicles)
    print("average number of non-served vehicles per day:", statistics.non_served_vehicles * 1440/run_time)
    print()


def overload_in_cable(run_time, loc, load_over_time, cable_threshold):
    overload_time = 0

    for i in range(len(load_over_time) - 1):
        if abs(load_over_time[i][1]) > cable_threshold * 1.1: #account for the 10% overload margin, absolute value in case solar generates too much power
            overload_time += load_over_time[i + 1][0] - load_over_time[i][0]

    if abs(load_over_time[-1][1]) > cable_threshold * 1.1:
        overload_time += run_time - load_over_time[-1][0]

    return overload_time/run_time


def overload_in_network(run_time, statistics):
    overload_intervals = []

    for loc, load_over_time in statistics.load_over_time.items():
        #get all seperate intervals with overload
        cable_threshold = 200 if loc != 9 else 1000

        for i in range(len(load_over_time) - 1):
            if load_over_time[i][1] > cable_threshold:
                overload_intervals.append((load_over_time[i][0], load_over_time[i + 1][0]))

        if load_over_time[-1][1] > cable_threshold:
            overload_intervals.append((load_over_time[-1][0], run_time))

    # Sorting based on the increasing order
    # of the start intervals
    sorted_intervals = sorted(overload_intervals, key=lambda x: x[0])
    merged = []

    for higher in sorted_intervals:
        if not merged:
            merged.append(higher)
        else:
            lower = merged[-1]
            # test for intersection between lower and higher:
            # we know via sorting that lower[0] <= higher[0]
            if higher[0] <= lower[1]:
                upper_bound = max(lower[1], higher[1])
                merged[-1] = (lower[0], upper_bound)  # replace by merged interval
            else:
                merged.append(higher)

    overload_time = sum([y - x for [x,y] in merged])

    return overload_time/run_time
