from statistics import Statistics

def calculate_average_measures(statistics, run_time, warm_up, solar_locations):
    # returns:
    # - avg delay percentage
    # - avg revenue per day
    # - avg percentage of time with overload on network

    days = len(statistics) - warm_up

    average_delays = list(map(lambda x : x.average_delay(), statistics[warm_up:]))
    average_revenues = list(map(lambda x : x.revenue(solar_locations)[0], statistics[warm_up:]))
    average_solar_revenues = list(map(lambda x : x.revenue(solar_locations)[1], statistics[warm_up:]))
    average_overload_percentages = list(map(lambda x : x.overload_in_network(run_time/days), statistics[warm_up:]))


    average_delay = sum(average_delays)/days
    average_revenue = sum(average_revenues)/days
    average_solar_revenue = sum(average_solar_revenues)/days
    average_overload_percentage =  sum(average_overload_percentages)/days

    return average_delay, average_revenue, average_solar_revenue, average_overload_percentage

def save_measures(statistics, run_time, warm_up, solar_locations, fname):
    measures = calculate_average_measures(statistics, run_time, warm_up, solar_locations)

    f = open(fname + " measures.txt", 'w')

    f.write("average_delay, average_revenue, average_solar_revenue average_overload_percentage\n")
    f.write("{} {} {} {}".format(*measures))

    f.close()

#takes a list of statistics and merges them, assuming they are ordered by time.
def merge_statistics(statistics):
    statistic = Statistics(None)
    for s in statistics:
        for loc, load_over_time in s.load_over_time.items():
            statistic.load_over_time[loc] += load_over_time

        statistic.solar_factor_over_time += s.solar_factor_over_time

        for loc, parked_vehicles_maximum in s.parked_vehicles_maximum.items():
            statistic.parked_vehicles_maximum[loc] = max(statistic.parked_vehicles_maximum[loc], parked_vehicles_maximum)

        statistic.non_served_vehicles += s.non_served_vehicles
        statistic.total_vehicles += s.total_vehicles

        statistic.total_delay_time += s.total_delay_time
        statistic.maximum_dalay_time = max(statistic.maximum_dalay_time, s.maximum_dalay_time)
        statistic.cars_with_delay += s.cars_with_delay

    return statistic

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
