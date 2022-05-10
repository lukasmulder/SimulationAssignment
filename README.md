TODO:
  - Event diagram
    - Solar changes and price changes result in events too
  - Poisson arrival times result in huge gap?
  - Input analysis
  - Make each car an individual entity
  - Implement more statistics
    - Departure delays
  - Implement different charging strategies
    - Price driven
    - First come first serve
    - Earliest latest feasible start time
  - Implement solar energy
    - Implement flow network model

Assumptions:
  - Cars have no travel time between parking spaces
  - Charging capacity is never limited
  - Parking choices are random (not influenced by relative distance)
  - Cars only leave when they are fully charged
  - If connection time is shorter than charging time, it is extended as much as necessary

Model:
  - State: Parking lots, charging network, cars
  - Events: arrival, finished charging, departure
  - Event diagram:         arrival
                          /       \
                         V         V
          finished charging       departure
