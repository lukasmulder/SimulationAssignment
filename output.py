from statistics import Statistics

def calculate_average_measures(statistics, run_time, warm_up, solar_locations):
    # returns:
    # - avg delay percentage
    # - avg revenue per day
    # - avg percentage of time with overload on network

    average_delay = 0
    average_revenue = 0
    average_overload_percentage = 0

    for statistic in statistics[warm_up:]:
        print(statistic.day)
        average_delay += statistic.average_delay()
        average_revenue += statistic.revenue(solar_locations)[0]
        average_overload_percentage += statistic.overload_in_network(run_time)

    average_delay /= len(statistics)
    average_revenue /= len(statistics)
    average_overload_percentage /= len(statistics)

    return average_delay, average_revenue, average_overload_percentage
