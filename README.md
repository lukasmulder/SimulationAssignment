TODO:
  - Make simulation model

Assumptions:
  - Cars have no travel time between parking spaces
  - Charging capacity is never limited
  - Parking choices are random (not influenced by relative distance)
  - Cars only leave when they are fully charged

Model:
  - State: Parking lots, charging network
  - Events: arrival, finished charging, departure
  - Event diagram:         arrival
                          /       \
                         V         V
          finished charging       departure
