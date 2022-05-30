from statistics import *
from output import *
import matplotlib.pyplot as plt

def plot_all_cable_loads(statistics, fname):
    days = statistics.day
    x = range(0, days * 24 * 60)
    plt.axhline(y=200, color='gray', linestyle='--')
    plt.axhline(y=220, color='r', linestyle='--')
    plt.axhline(y=1000, color='gray', linestyle='--')
    plt.axhline(y=1100, color='y', linestyle='--')
    plt.fill_between(x, 200, 220,color='gray', alpha=0.2)
    plt.fill_between(x, 1000, 1100,color='gray', alpha=0.2)

    for cable, load_over_t in statistics.load_over_time.items():
        label = "cable " + str(cable) if cable != 9 else "main cable"
        plt.plot([x[0] for x in load_over_t], [x[1] for x in load_over_t], label = label)


    plt.xlabel("Time (minutes)")
    plt.ylabel("Load over main cable and solar load (kWh)")
    plt.legend()
    #plt.savefig('/home/lukas/Documents/UU/Optimization_for_Sustainability/SimulationAssignment/results/figs/{}.pdf'.format(fname), bbox_inches='tight')
    plt.show()
    
def plot_main_cable(statistics,fname):
    days = statistics.day
    x = range(0, days * 24 * 60)
    plt.axhline(y=1000, color='gray', linestyle='--')
    plt.fill_between(x, 1000, 1100,color='gray', alpha=0.2)
    
    _, load_over_t = statistics.load_over_time.items()[8]
    label = "main cable"
    plt.plot([x[0] for x in load_over_t], [x[1] for x in load_over_t], label = label)
    
