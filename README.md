TODO:
  - Output analysis

Cat:
  - model schrijven
  - confidence lezen en implementeren

Lukas:
  - graphs
  - tabellen
    - Solar placement vs. season & strat -> cost, delay
  - run 1 maand (ez)

Questions:
  - Price changes as events?
  - Does ELFS also try to actively minimize overloads
  - Expected departure time vs. real departure time

Assumptions:
  - Cars have no travel time between parking spaces
  - Charging capacity is never limited
  - Parking choices are random (not influenced by relative distance)
  - Cars only leave when they are fully charged
  - If connection time is shorter than charging time, it is extended as much as necessary
  - Cars do not care about the queue when picking a parking space for the FCFS strategy
  - Cars know the times of energy price changes
  - Cars do not queue for an empty parking spot
  - Rate change is applied instantly and starts a new proces
  - for ELFS: first car is prioritized, otherwise first in line that does not "get in the way" of the first in line
  - Global queue assumption
  - surplus solar energy is lost

Model:
  - State: Parking lots, charging network, cars
  - Events:
    - Arrival
    - Parking
    - Start charging
    - Stop charging
    - (Expected finish)
    - Finished charging
    - Departure
    - Solar change
    - Price change
