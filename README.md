# Smart Heating Controller Simulation
## Description
These files provide a simulation environment for a smart heating controller. To run it run the temp_server.py file as well as the controller.py file.

The test runs are designed to run for scenarios of one day. The sim_data folder contains examples for Weather Data and Occupancy Simulation as well as Occupancy Prediction. The WeatherData files are used by the weather module as well as the temp_server. Both should use the same data for a run. In the occupancy_simulation files for occupancy sensing and occupancy prediction are read in.

To change the simulation models parameters edit them in the temp_server file.

The programm produces outputs of the setpoints chosen as well as the simulated temperatures.


##Prerequisites
The program only runs using Python3.4 and the aiocoap must be included or installed it can be downloaded here:
https://github.com/chrysn/aiocoap