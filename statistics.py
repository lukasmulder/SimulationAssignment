import matplotlib.pyplot as plt

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

        self.solar_factor_over_time = []

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

def update_solar_statistics(current_time, statistics, energy):
    statistics.solar_factor_over_time.append((current_time, energy))

def update_delay_statistics(statistics, current_time, car):
    arrival_time = car.arrival_time
    connection_time = car.connection_time
    delay = current_time - arrival_time - connection_time
    if delay > 0:
        statistics.total_delay_time += delay
        statistics.maximum_dalay_time = max(delay, statistics.maximum_dalay_time)
        statistics.cars_with_delay += 1

def generate_report(run_time, state, statistics, season, solar_locations, strategy, fname):
    f = open(fname + " report.txt", 'w')
    if solar_locations != []:
        f.write("solar locations: {} \nseason: {} \nstrategy: {}\n".format(solar_locations, season, strategy))
    else:
        f.write("base case \nstrategy: {}\n".format(strategy))
    f.write("run time was: {} minutes ({} hours)\n".format(run_time, run_time/60))

    f.write("---------------------------------------------\n")

    for loc, parked_vehicles_maximum in statistics.parked_vehicles_maximum.items():
        f.write("parked vehicles maximum on parking {}: {}/{}\n".format(loc, parked_vehicles_maximum, state.parking[loc].capacity))

    f.write("---------------------------------------------\n")

    f.write("percentage of vehicles with a delay: {}%\n".format(100*statistics.cars_with_delay/statistics.total_vehicles))
    f.write("average delay over all vehicles: {} minutes\n".format(statistics.total_delay_time/statistics.total_vehicles))
    f.write("maximum delay: {} minutes\n".format(statistics.maximum_dalay_time))

    f.write("---------------------------------------------\n")

    for loc, load_over_time in statistics.load_over_time.items():
        f.write( "max load of cable {}: {}\n".format(loc, max( [abs(x[1]) for x in load_over_time] ) ) )

    f.write("---------------------------------------------\n")

    for loc, load_over_time in statistics.load_over_time.items():
        cable_threshold = 200 if loc != 9 else 1000 #set cable cable_threshold according to which cable it is
        f.write( "overload of cable {}: {}\n".format(loc, overload_in_cable(run_time, loc, load_over_time, cable_threshold) ) )

    f.write("overload of network: {}\n".format(overload_in_network(run_time, statistics)) )

    f.write("---------------------------------------------\n")

    f.write("total number of vehicles: {}\n".format( statistics.total_vehicles) )
    f.write("fraction of non-served vehicles: {}\n".format( statistics.non_served_vehicles/statistics.total_vehicles) )
    f.write("average number of non-served vehicles per day: {}\n".format( statistics.non_served_vehicles * 1440/run_time) )
    f.close()

def save_data(run_time, state, statistics, season, solar_locations, strategy, fname):
    f = open(fname + " data.txt", 'w')
    if solar_locations != []:
        f.write("solar locations: {}, season: {}, strategy: {}, run time: {}\n".format(solar_locations, season, strategy, run_time))
    else:
        f.write("base case, strategy: {}, run time: {}\n".format(strategy, run_time))

    f.write("parked vehicles maximum on parking (parking, maximum, capacity)\n")
    for loc, parked_vehicles_maximum in statistics.parked_vehicles_maximum.items():
        f.write("{} {} {}\n".format(loc, parked_vehicles_maximum, state.parking[loc].capacity))


    f.write("percentage of vehicles with a delay\n{}\n".format(100*statistics.cars_with_delay/statistics.total_vehicles))
    f.write("average delay over all vehicles\n{} \n".format(statistics.total_delay_time/statistics.total_vehicles))
    f.write("maximum delay\n{} \n".format(statistics.maximum_dalay_time))

    f.write( "max load of cable (cable, load)" )
    for loc, load_over_time in statistics.load_over_time.items():
        f.write( "{} {}\n".format(loc, max( [abs(x[1]) for x in load_over_time] ) ) )


    f.write("overload of cable (cable, overload percentage)")
    for loc, load_over_time in statistics.load_over_time.items():
        cable_threshold = 200 if loc != 9 else 1000 #set cable cable_threshold according to which cable it is
        f.write( "{} {}\n".format(loc, overload_in_cable(run_time, loc, load_over_time, cable_threshold) ) )

    f.write("overload of network \n{}\n".format(overload_in_network(run_time, statistics)) )

    f.write("total number of vehicles\n{}\n".format( statistics.total_vehicles) )
    f.write("fraction of non-served vehicles\n{}\n".format( statistics.non_served_vehicles/statistics.total_vehicles) )
    f.write("average number of non-served vehicles per day\n{}\n".format( statistics.non_served_vehicles * 1440/run_time) )
    f.close()

def dump_load_over_time(statistics):
    f = open("./results/load_over_time.txt", "w")
    for loc, load_over_time in statistics.load_over_time.items():
        f.write("location: {}\n".format(loc))
        for x in load_over_time:
            f.write("{}; {}\n".format(x[0],x[1]))
        f.write("\n")

def plot_load_over_time(statistics) :
    for loc, load_over_time in statistics.load_over_time.items():
        plt.subplot(2,5,loc + 1)
        plt.plot([x[0] for x in load_over_time], [x[1] for x in load_over_time])
    plt.show()

def plot_solar_over_time(statistics, solar_locations):
    plt.plot([x[0] for x in statistics.solar_factor_over_time], [x[1]*200*len(solar_locations) for x in statistics.solar_factor_over_time])
    plt.show()

def plot_solar_percentage_over_time(statistics, solar_locations):
    num_of_panels = len(solar_locations)
    fractions = []
    i = 0
    for load in statistics.load_over_time[9]:
        if statistics.solar_factor_over_time[i][0] <= load[0] and i + 1 < len(statistics.solar_factor_over_time):
            i += 1
        solar_factor = statistics.solar_factor_over_time[i][1]
        solar = solar_factor * 200 * num_of_panels

        fraction = solar/(solar + load[1])
        fractions.append((load[0], fraction))

    plt.plot([x[0] for x in fractions], [x[1]*len(solar_locations) for x in fractions])
    #plt.plot([x[0] for x in statistics.solar_factor_over_time], [x[1]*200*len(solar_locations) for x in statistics.solar_factor_over_time])
    plt.show()

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
