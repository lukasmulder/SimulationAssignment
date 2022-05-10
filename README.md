TODO:
  - Input analysis
  - Implement different charging strategies
    - Price driven
    - First come first serve
    - Earliest latest feasible start time
  - Implement more statistics
    - Departure delays
    - Non-served vehicles
  - Implement solar energy

Assumptions:
  - Cars have no travel time between parking spaces
  - Charging capacity is never limited
  - Parking choices are random (not influenced by relative distance)
  - Cars only leave when they are fully charged
  - If connection time is shorter than charging time, it is extended as much as necessary

Model:
  - State: Parking lots, charging network
  - Events: arrival, finished charging, departure
  - Event diagram:         arrival
                          /       \
                         V         V
          finished charging       departure
