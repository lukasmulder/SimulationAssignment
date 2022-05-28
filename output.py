from statistics import Statistics, all_pairwise_comparison, comparison_with_standard

def calculate_average_measures(statistics, run_time, warm_up, solar_locations):
    # returns:
        # ["./results/average_delay.csv",
        #  "./results/average_max_delay.csv",
        #  "./results/average_delay_fraction.csv",
        #  "./results/average_revenue.csv",
        #  "./results/average_solar_revenue.csv",
        #  "./results/average_overload.csv",
        #  "./results/average_max_load.csv",
        #  "./results/average_served.csv"
        #  "./results/average_non_served.csv",
        #  "./results/average_fraction_non_served.csv"

    days = len(statistics) - warm_up

    measures = []

    average_delays = list(map(lambda x : x.average_delay(), statistics[warm_up:]))
    measures.append(average_delays)
    average_max_delays = list(map(lambda x : x.maximum_dalay_time, statistics[warm_up:]))
    measures.append(average_max_delays)
    average_delay_fractions = list(map(lambda x : x.cars_with_delay/x.total_vehicles, statistics[warm_up:]))
    measures.append(average_delay_fractions)

    average_revenues = list(map(lambda x : x.revenue(solar_locations)[0], statistics[warm_up:]))
    measures.append(average_revenues)
    average_solar_revenues = list(map(lambda x : x.revenue(solar_locations)[1], statistics[warm_up:]))
    measures.append(average_solar_revenues)

    average_overload_percentages = list(map(lambda x : x.overload_in_network(run_time/days), statistics[warm_up:]))
    measures.append(average_overload_percentages)
    average_max_loads = list(map(lambda x : x.max_load(9), statistics[warm_up:]))
    measures.append(average_max_loads)

    average_serveds = list(map(lambda x : x.total_vehicles - x.non_served_vehicles, statistics[warm_up:]))
    measures.append(average_serveds)
    average_non_serveds = list(map(lambda x : x.non_served_vehicles, statistics[warm_up:]))
    measures.append(average_non_serveds)
    average_fraction_non_serveds = list(map(lambda x : x.non_served_vehicles/x.total_vehicles, statistics[warm_up:]))
    measures.append(average_fraction_non_serveds)

    measures = list(map(lambda x : sum(x)/days, measures))

    # average_delay = sum(average_delays)/days
    # average_max_delay = sum(average_max_delays)/days
    # average_delay_fraction = sum(average_delay_fractions)/days
    #
    # average_revenue = sum(average_revenues)/days
    # average_solar_revenue = sum(average_solar_revenues)/days
    #
    # average_overload_percentage = sum(average_overload_percentages)/days
    # average_max_load = sum(average_max_loads)/days
    #
    # average_served = sum(average_serveds)/days
    # average_non_served = sum(average_non_serveds)/days
    # average_fraction_non_served = sum(average_fraction_non_serveds)/days

    return measures

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

def _save_data(run_time, state, statistics, season, solar_locations, strategy, fname):
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

def save_data(run_time, warm_up, s_statistics, w_statistics, solar_locations, strategy):
    s_measures = calculate_average_measures(s_statistics, run_time, warm_up, solar_locations)
    w_measures = calculate_average_measures(w_statistics, run_time, warm_up, solar_locations)

    paths = ["average_delay",
             "average_max_delay",
             "average_delay_fraction",
             "average_revenue",
             "average_solar_revenue",
             "average_overload",
             "average_max_load",
             "average_served",
             "average_non_served",
             "average_fraction_non_served"
             ]

    strategy_dict = {1:"Base", 2:"Price driven",3:"FCFS",4:"ELFS"}
    strategy_str = strategy_dict[strategy]

    for i in range(len(paths)):
        path = paths[i]
        f = open("./results/" + path + ".tex", "a")
        if len(solar_locations) == 0:
            s = format_float(s_measures[i])
            w = format_float(w_measures[i])
            a = format_float((s_measures[i]+w_measures[i])/2)
            f.write(strategy_str + "&{}&{}&{}&".format(s,w,a))
        elif len(solar_locations) == 4:
            s = format_float(s_measures[i])
            w = format_float(w_measures[i])
            a = format_float((s_measures[i]+w_measures[i])/2)
            f.write("{}&{}&{} \\\\ \n".format(s,w,a))
        else:
            s = format_float(s_measures[i])
            w = format_float(w_measures[i])
            a = format_float((s_measures[i]+w_measures[i])/2)
            f.write("{}&{}&{}&".format(s,w,a))
        f.close()

def format_float(x):
    s = "{:.2f}".format(x)[0:6]
    if s[-1] == '.':
        s = s[:-1]
    return s

def prepare_save_files(run_time, warm_up):
    paths = ["average_delay",
             "average_max_delay",
             "average_delay_fraction",
             "average_revenue",
             "average_solar_revenue",
             "average_overload",
             "average_max_load",
             "average_served",
             "average_non_served",
             "average_fraction_non_served"
             ]

    #prepare the files
    for path in paths:
        f = open("./results/" + path + ".tex", "w")
        f.write("%" + path + "\n")
        f.write("%run time: {}, warm up: {}\n".format(run_time, warm_up))
        f.write("\\begin{table}[h] \n\\centering \n\\begin{tabular}{l|lll|lll|lll}")
        f.write("Number of \\\\ solar panels&0& & &2& & &4& & \\\\ \hline \n")
        f.write("Season or average & S & W & A & S & W & A & S & W & A \\\\ \hline \n")
        f.close()

def close_save_files():
    paths = ["average_delay",
             "average_max_delay",
             "average_delay_fraction",
             "average_revenue",
             "average_solar_revenue",
             "average_overload",
             "average_max_load",
             "average_served",
             "average_non_served",
             "average_fraction_non_served"
             ]
    for path in paths:
        f = open("./results/" + path + ".tex", "a")
        f.write("\\end{tabular} \n\\end{table}")
        f.close()

# takes all statistics from a run and computes:
# - All pairwise combinations
# - Comparison with a standard
# - revenue
# - average delay
# - percentage of non-served vehicles
# - percentage of time with blackout
# - (inter-cable blackout percentage comparison)
def compute_statistics(all_statistics, standard, confidence):
    data = all_statistics.items()

    revenues = [(name, [s.revenue([])[0] for s in ss]) for (name, ss) in data]                #list(map(lambda x : x.revenue([])[0], d)))
    average_delays = [(name, [s.average_delay() for s in ss]) for (name, ss) in data]
    fraction_non_served = [(name, [s.non_served_vehicles_fraction() for s in ss]) for (name, ss) in data]
    fraction_blackout = [(name, [s.overload_in_network(24*60) for s in ss]) for (name, ss) in data]

    measures = [("revenue", revenues, (standard[0], [s.revenue([])[0] for s in standard[1]])),
                ("average_delays", average_delays, (standard[0], [s.average_delay() for s in standard[1]])),
                ("fraction_non_served",fraction_non_served, (standard[0], [s.non_served_vehicles_fraction() for s in standard[1]])),
                ("fraction_blackout", fraction_blackout, (standard[0], [s.overload_in_network(24*60) for s in standard[1]])  )
                ]

    f = open("./results/confidence_intervals.txt", "w")
    for n, m, s in measures:
        f.write(n + "\n\n")
        f.write("Pairwise comparison\n\n")
        for x in all_pairwise_comparison(m, confidence):
            f.write(",".join(str(item) for item in x))
            f.write("\n")
        f.write("Comparison with standard\n\n")
        for x in comparison_with_standard(s, m, confidence):
            f.write(",".join(str(item) for item in x))
            f.write("\n")
    f.close()
