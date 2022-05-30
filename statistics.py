from helper import convert_time_price, revenue
import matplotlib.pyplot as plt
import numpy as np, scipy.stats as st

class Statistics:
    def __init__(self, day):
        self.day = day

        self.load_over_time = { 0 : []
                              , 1 : []
                              , 2 : []
                              , 3 : []
                              , 4 : []
                              , 5 : []
                              , 6 : []
                              , 7 : []
                              , 8 : []
                              , 9 : []
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

    def non_served_vehicles_fraction(self):
        return self.non_served_vehicles/self.total_vehicles

    def non_served_vehicles_average(self, run_time):
        self.non_served_vehicles * 1440/run_time

    def delay_percentage(self):
        return 100*self.cars_with_delay/self.total_vehicles

    def average_delay(self):
        return self.total_delay_time/self.total_vehicles

    def max_load(self, loc):
        return max( [abs(x[1]) for x in self.load_over_time[loc]]  )

    def overload_in_cable(self, run_time, loc, cable_threshold):
        overload_time = 0
        load_over_t = self.load_over_time[loc]

        for i in range(len(self.load_over_time[loc]) - 1):
            if abs(load_over_t[i][1]) > cable_threshold * 1.1: #account for the 10% overload margin, absolute value in case solar generates too much power
                overload_time += load_over_t[i + 1][0] - load_over_t[i][0]

        if abs(load_over_t[-1][1]) > cable_threshold * 1.1:
            overload_time += run_time - load_over_t[-1][0]

        return overload_time/run_time

    def overload_in_network(self, run_time):
        overload_intervals = []

        for loc, load_over_time in self.load_over_time.items():
            #get all seperate intervals with overload
            cable_threshold = 200 if loc != 9 else 1000

            for i in range(len(load_over_time) - 1):
                if abs(load_over_time[i][1]) > cable_threshold:
                    overload_intervals.append((load_over_time[i][0], load_over_time[i + 1][0]))

            if abs(load_over_time[-1][1]) > cable_threshold:
                overload_intervals.append((load_over_time[-1][0], run_time))

        # Sorting based on the increasing order
        # of the start intervals
        sorted_intervals = sorted(overload_intervals, key = lambda x: x[0])
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

    def solar_over_time(self, solar_locations):
        # returns a list of the solar production over time
        num_of_panels = len(solar_locations)
        solar_over_t = []
        i = 0
        for load in self.load_over_time[9]:
            if self.solar_factor_over_time[i][0] <= load[0] and i + 1 < len(self.solar_factor_over_time):
                i += 1
            solar_factor = self.solar_factor_over_time[i][1]
            solar = solar_factor * 200 * num_of_panels

            solar_over_t.append((load[0], solar))

        return solar_over_t

    def total_demand_over_time(self, solar_locations):
        # returns the total demand over time
        total_demand_over_t = []
        load_over_t = self.load_over_time[9]
        solar_over_t = self.solar_over_time(solar_locations)
        for i in range(len(load_over_t)):
            time = load_over_t[i][0]
            x = load_over_t[i][1]
            y = solar_over_t[i][1]
            total_demand_over_t.append((time,x+y))
        return total_demand_over_t

    def solar_fraction_over_time(self, solar_locations):
        solar_fraction_over_t = []
        demand_over_t = self.total_demand_over_time(solar_locations)
        solar_over_t = self.solar_over_time(solar_locations)
        for i in range(len(demand_over_t)):
            time = demand_over_t[i][0]
            x = solar_over_t[i][1]
            y = demand_over_t[i][1]
            solar_fraction_over_t.append((time,x/y))
        return solar_fraction_over_t

    def revenue(self, solar_locations):
        solar_fraction_over_t = self.solar_fraction_over_time(solar_locations)
        total_demand_over_t = self.total_demand_over_time(solar_locations)

        revenue = 0
        solar_revenue = 0

        for i in range(0,len(total_demand_over_t)-1):
            duration = total_demand_over_t[i+1][0] - total_demand_over_t[i][0]
            demand = total_demand_over_t[i][1]
            price = convert_time_price(total_demand_over_t[i][0])
            revenue += demand * price * duration / 60 # transform to kWh
            solar_revenue += solar_fraction_over_t[i][1] * demand * price * duration / 60 # transform to kWh

        return revenue, solar_revenue



def update_parking_statistics(statistics, parking):
    for key, loc in parking.items():
        if statistics.parked_vehicles_maximum[key] < len(loc.cars):
            statistics.parked_vehicles_maximum[key] = len(loc.cars)

def update_load_statistics(current_time, statistics, cables):
    for loc, load_over_time in statistics.load_over_time.items():
        if (load_over_time == []) or (load_over_time[-1][1] != cables[loc].flow): #only append the array if the load over a cable changes
            load_over_time.append( (current_time, cables[loc].flow) )

def update_solar_statistics(current_time, statistics, energy):
    statistics.solar_factor_over_time.append((current_time, energy))

def update_delay_statistics(statistics, current_time, car):
    arrival_time = car.arrival_time
    connection_time = car.connection_time
    delay = current_time - arrival_time - connection_time
    if delay > 0.001:
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

    f.write("percentage of vehicles with a delay: {}%\n".format(statistics.delay_percentage()))
    f.write("average delay over all vehicles: {} minutes\n".format(statistics.average_delay()))
    f.write("maximum delay: {} minutes\n".format(statistics.maximum_dalay_time))

    f.write("---------------------------------------------\n")

    for loc, _ in statistics.load_over_time.items():
        f.write( "max load of cable {}: {}\n".format(loc, statistics.max_load(loc)))

    f.write("---------------------------------------------\n")

    for loc, load_over_time in statistics.load_over_time.items():
        cable_threshold = 200 if loc != 9 else 1000 #set cable cable_threshold according to which cable it is
        f.write( "overload of cable {}: {}\n".format(loc, statistics.overload_in_cable(run_time, loc, cable_threshold) ) )

    f.write("overload of network: {}\n".format(statistics.overload_in_network(run_time)) )

    f.write("---------------------------------------------\n")

    revenue, solar_revenue = statistics.revenue(solar_locations)
    f.write("total revenue: {}, of which solar revenue: {}\n".format(revenue, solar_revenue))

    f.write("---------------------------------------------\n")

    f.write("total number of vehicles: {}\n".format( statistics.total_vehicles) )
    f.write("fraction of non-served vehicles: {}\n".format( statistics.non_served_vehicles_fraction() ) )
    f.write("average number of non-served vehicles per day: {}\n".format( statistics.non_served_vehicles_average(run_time)) )
    f.close()

def dump_load_over_time(statistics):
    f = open("./results/load_over_time.txt", "w")
    for loc, load_over_time in statistics.load_over_time.items():
        f.write("location: {}\n".format(loc))
        for x in load_over_time:
            f.write("{}; {}\n".format(x[0],x[1]))
        f.write("\n")

def plot_load_over_time(statistics, solar_locations, fname) :
    # for loc, load_over_time in statistics.load_over_time.items():
    #     plt.subplot(2,5,loc + 1)
    #     plt.plot([x[0] for x in load_over_time], [x[1] for x in load_over_time])
    load_over_t = statistics.load_over_time[9]
    solar_over_t = statistics.solar_over_time(solar_locations)

    plt.plot([x[0] for x in load_over_t], [x[1] for x in load_over_t])
    plt.plot([x[0] for x in solar_over_t], [x[1] for x in solar_over_t])
    plt.xlabel("Time (minutes)")
    plt.ylabel("Load over main cable and solar load (kWh)")
    # plt.savefig('/home/lukas/Documents/UU/Optimization_for_Sustainability/SimulationAssignment/results/figs/{}.pdf'.format(fname), bbox_inches='tight')
    plt.clf()
    plt.show()

def plot_solar_over_time(statistics, solar_locations):
    plt.plot([x[0] for x in statistics.solar_factor_over_time], [x[1]*200*len(solar_locations) for x in statistics.solar_factor_over_time])
    plt.show()

#calculates confidence interval of data1 - data 2 with confidence = confidence
def confidence_interval(data1, data2, confidence):
    a = [x-y for x,y in zip(data1,data2)]
    interval = st.t.interval(confidence, len(a)-1, loc=np.mean(a), scale=st.sem(a))
    return interval

#retursn 2d list with index (index data 1, index data 2) and confidence interval
def all_pairwise_comparison(data, confidence):
    k = len(data)
    number_of_intervals = int(k*(k-1)/2)
    intervals = [ [0]*k for i in range(k)]

    for i in range(k):
        namei,datai = data[i]
        for j in range(k):

            namej,dataj = data[j]

            intervals[i][j] = (namei + " vs "+namej,confidence_interval(datai,dataj,1- (1-confidence)/number_of_intervals))

    return intervals

#returns confidence intervals for comparing elements in data to standard
def comparison_with_standard(standard, data, confidence):
    intervals = []
    namestandard, standarddata = standard

    for i in range(len(data)):
        namecurrent, currentdata = data[i]
        intervals.append((namestandard+" vs "+namecurrent,confidence_interval(standarddata, currentdata, 1-(1-confidence)/(len(data)))))

    return intervals

def plot_confidence_intervals(intervals_list, horizontal_line_width = 0.25, color = '#2187bb'):
    num_of_plots = len(intervals_list)
    for i in range(num_of_plots):
        intervals = intervals_list[i][1]
        plt.subplot(1,num_of_plots,i+1)
        x = 0
        names = []
        for name, interval in intervals:
            x += 1
            names.append(name)
            bottom,top = interval
            mean = bottom+(top-bottom)/2
            left = x - horizontal_line_width / 2
            right = x + horizontal_line_width / 2
            plt.plot([x, x], [top, bottom], color=color)
            plt.plot([left, right], [top, top], color=color)
            plt.plot([left, right], [bottom, bottom], color=color)
            plt.plot(x, mean, 'o', color='#f44336')
            
        plt.xticks(range(1,len(intervals)+1), names)
        plt.title(str(intervals_list[i][0]))
    plt.show()
