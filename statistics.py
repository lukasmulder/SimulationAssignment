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

def update_statistics(current_time, statistics, parking, cables):
    for loc, load_over_time in statistics.load_over_time.items():
        if (load_over_time[-1][1] != cables[loc].flow): #only append the array if the load over a cable changes
            load_over_time.append( (current_time, cables[loc].flow) )

def generate_report(statistics, run_time):
    print("End of simulation, runtime was:", run_time)

    for loc, load_over_time in statistics.load_over_time.items():
        print( "max load of cable", loc, max( [x[1] for x in load_over_time] ) )

    for loc, load_over_time in statistics.load_over_time.items():
        print( "load over time of cable", loc, load_over_time )

    for loc, load_over_time in statistics.load_over_time.items():
        cable_threshold = 20 if loc != 9 else 100 #set cable cable_threshold according to which cable it is
        print( "overload of cable", loc, overload(run_time, loc, load_over_time, cable_threshold) )

def overload(run_time, loc, load_over_time, cable_threshold):
    overload_time = 0

    for i in range(len(load_over_time) - 1):
        if load_over_time[i][1] > cable_threshold:
            overload_time += load_over_time[i + 1][0] - load_over_time[i][0]

    if load_over_time[-1][1] > cable_threshold:
        overload_time += run_time - load_over_time[-1][0]

    return overload_time/run_time
