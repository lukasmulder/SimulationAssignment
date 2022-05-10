TODO:
  - Implement different charging strategies
    - Price driven
    - First come first serve
    - Earliest latest feasible start time
  - Input analysis
  - Implement more statistics
    - Departure delays
    - Non-served vehicles
  - Implement solar energy

Assumptions:
  - Cars have no travel time
  - Charging capacity is never limited
  - If connection time is shorter than charging time, extend it until it is enough

Model:
  - State: Parking lots, charging network
  - Events: arrival, finished charging, departure
  - Event diagram:         arrival
                          /       \
                         V         V
          finished charging       departure
