from statistics import *
from helper import format_float
from plotting import *

# calculates daily averages of:
# - delays
# - max delays
# - fraction with delay
# - revenue
# - revenue from solar panels
# - overload fraction
# - max load
# - served
# - non served
# - fraction non-served
#
# and returns them in a list.
def calculate_average_measures(statistics, run_time, warm_up, solar_locations):

    days = len(statistics) - warm_up

    measures = []

    # fill the list with data
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

    # take the average
    measures = list(map(lambda x : sum(x)/days, measures))

    return measures

# function for saaving the measures to a text file
# probably outdated since the formatting has changed in the meantime.
def save_measures(statistics, run_time, warm_up, solar_locations, fname):
    measures = calculate_average_measures(statistics, run_time, warm_up, solar_locations)

    f = open(fname + " measures.txt", 'w')

    f.write("average_delay, average_revenue, average_solar_revenue average_overload_percentage\n")
    f.write("{} {} {} {}".format(*measures))

    f.close()

# function for saving all the data, formatted as LaTeX tables.
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

# makes the headers for the LaTeX tables
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

# makes the footers for the LaTeX tables
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
def compute_statistics(all_statistics, standard_summer, standard_winter, standard_strat_3, standard_strat_4, confidence):

    standards = (standard_summer,  all_statistics[standard_summer])
    standardw = (standard_winter,  all_statistics[standard_winter])

    scenarios_summer = ["{}{}{}".format(solar_location, strategy, "summer") for solar_location in [[],[6,7], [1,2,6,7]] for strategy in [3,4]]
    scenarios_winter = ["{}{}{}".format(solar_location, strategy, "winter") for solar_location in [[],[6,7], [1,2,6,7]] for strategy in [3,4]]

    scenarios_summer.remove(standard_summer)
    scenarios_winter.remove(standard_winter)

    data = all_statistics.items()

    revenues = [(name, [s.revenue([])[0] for s in ss]) for (name, ss) in data]
    average_delays = [(name, [s.average_delay() for s in ss]) for (name, ss) in data]
    fraction_non_served = [(name, [s.non_served_vehicles_fraction() for s in ss]) for (name, ss) in data]
    fraction_blackout = [(name, [s.overload_in_network(24*60) for s in ss]) for (name, ss) in data]

    # saves the above computed measure with a label and a formatted standard to compare it to.
    measures = [("revenue", revenues, (standards[0], [s.revenue([])[0] for s in standards[1]]),  (standardw[0], [s.revenue([])[0] for s in standardw[1]]) ),
                ("average_delays", average_delays, (standards[0], [s.average_delay() for s in standards[1]]), (standardw[0], [s.average_delay() for s in standardw[1]]) ),
                ("fraction_non_served",fraction_non_served, (standards[0], [s.non_served_vehicles_fraction() for s in standards[1]]), (standardw[0], [s.non_served_vehicles_fraction() for s in standardw[1]]) )]

    intervals_list_summer = []
    intervals_list_winter = []

    # make confidence intervals for first reserach question.
    for n, m, ss, ws in measures:
        mfilteredsummer = list(filter(lambda x : x[0] in scenarios_summer, m))
        mfilteredwinter = list(filter(lambda x : x[0] in scenarios_winter, m))
        intervalssummer = comparison_with_standard(ss, mfilteredsummer, confidence)
        intervalswinter = comparison_with_standard(ws, mfilteredwinter, confidence)
        intervals_list_summer.append((n+" summer", intervalssummer))
        intervals_list_winter.append((n+" winter", intervalswinter))

    plot_confidence_intervals(intervals_list_summer, standards)
    plot_confidence_intervals(intervals_list_winter, standardw)

    # make plots for second research question.
    scenarios3s = ["{}{}{}".format(solar_location, 3, "summer") for solar_location in [[6,7], [1,2,6,7]] ]
    scenarios4s = ["{}{}{}".format(solar_location, 4, "summer") for solar_location in [[6,7], [1,2,6,7]] ]
    scenarios3w = ["{}{}{}".format(solar_location, 3, "winter") for solar_location in [[6,7], [1,2,6,7]] ]
    scenarios4w = ["{}{}{}".format(solar_location, 4, "winter") for solar_location in [[6,7], [1,2,6,7]] ]

    fraction_blackout_filtered3s = list(filter(lambda x : x[0] in scenarios3s, fraction_blackout))
    fraction_blackout_filtered4s = list(filter(lambda x : x[0] in scenarios4s, fraction_blackout))
    fraction_blackout_filtered3w = list(filter(lambda x : x[0] in scenarios3w, fraction_blackout))
    fraction_blackout_filtered4w = list(filter(lambda x : x[0] in scenarios4w, fraction_blackout))

    intervals3s = comparison_with_standard((standard_strat_3[0], [s.overload_in_network(24*60) for s in standard_strat_3[1]]) ,fraction_blackout_filtered3s, confidence )
    intervals4s = comparison_with_standard((standard_strat_4[0], [s.overload_in_network(24*60) for s in standard_strat_4[1]]) ,fraction_blackout_filtered4s, confidence )
    intervals3w = comparison_with_standard((standard_strat_3[0], [s.overload_in_network(24*60) for s in standard_strat_3[1]]) ,fraction_blackout_filtered3w, confidence )
    intervals4w = comparison_with_standard((standard_strat_4[0], [s.overload_in_network(24*60) for s in standard_strat_4[1]]) ,fraction_blackout_filtered4w, confidence )

    plot_confidence_intervals([ ("fraction_blackout_FCFS_summer",  intervals3s) ], standard_strat_3)
    plot_confidence_intervals([ ("fraction_blackout_ELFS_summer",  intervals4s) ], standard_strat_4)
    plot_confidence_intervals([ ("fraction_blackout_FCFS_winter",  intervals3w) ], standard_strat_3)
    plot_confidence_intervals([ ("fraction_blackout_ELFS_winter",  intervals4w) ], standard_strat_4)
