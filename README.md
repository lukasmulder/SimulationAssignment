TODO:
  - implement statistics


Assumptions:
  - Cars have no travel time
  - Charging capacity is never limited

Model:
  - State: Parking lots, charging network
  - Events: arrival, finished charging, departure
  - Event diagram:         arrival
                          /       \
                         V         V
          finished charging       departure
