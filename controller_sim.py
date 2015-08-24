"""
Implement MPC
"""
import sched
import time
from weather import WeatherService
from building import Building
import occupancy_simulation as occupancy
import datetime
import csv
import sqlite3

SETTINGS = {
    "time_interval": 0.01,
    "comfort_setpoint": 21.0,
    "setback_setpoint": 18.0,
}

init_rc = 100000
init_rq = 40

algorithm = 1

recorded_temperatures = []
setpoints = ["21.0"]
outdoor_temperatures = []


def initialize_dbs():
    # Controller DB storing recorded temperatures
    # and current configurations of the model
    conn = sqlite3.connect('dbs/controller.db')
    c = conn.cursor()
    # Create table for temp recordings if non existant
    query = "CREATE TABLE IF NOT EXISTS 'intervals' (first_temp real, last_temp real, heating integer)"
    c.execute(query)
    # Create table for configuration if non existant
    query = "CREATE TABLE IF NOT EXISTS 'model_config' (value real, name text)"
    c.execute(query)
    # Initialize values for configuration if non existent
    query = "SELECT * FROM model_config"
    c.execute(query)
    if not len(c.fetchall()):
        # No values have been initialized
        print("INITIALIZING VALUES")
        values = [(init_rc, 'rc'),
                  (init_rq, 'rq'),
                  (0, 'num_heating'),
                  (0, 'num_non_heating'),
                  ]
        query = "INSERT INTO model_config VALUES (?,?)"
        c.executemany(query, values)
    conn.commit()
    conn.close()


def choose_setpoint(building, weather_service, now, sc):
    # Decide how Long it takes to heat the house
    # Factors: Current Temperature, Model, Outside
    # Temperature, (Solar Gain) --> heat_time
    global recorded_temperatures, setpoints, outdoor_temperature

    ot = weather_service.get_current_temperature()
    outdoor_temperatures.append(ot)

    if occupancy.is_occupied(now):
        free_time = 0
    else:
        free_time = occupancy.get_next_pred_occupied_slot(now)

    """
    Algorithm 1 Approach
    """

    if algorithm == 1:
        heat_time = building.get_heat_time(ot, SETTINGS["comfort_setpoint"])
        print("TimeSlot: ", str(now.hour) + ":" + str(now.minute))
        print("Current Temperature: ", building.get_temperature())
        print("FreeTime: ", free_time)
        print("HeatTime: ", heat_time)
        if heat_time + 15 >= free_time:
            building.set_setpoint(SETTINGS["comfort_setpoint"])
            setpoints.append(SETTINGS["comfort_setpoint"])
            print ("Setpoint: 21")
        else:
            building.set_setpoint(SETTINGS["setback_setpoint"])
            setpoints.append(SETTINGS["setback_setpoint"])
            print ("Setpoint: 18")

    """
    Algorithm 2 Approach
    """
    if algorithm == 2:
        if free_time < 15:
            building.get_next_setpoint(ot, SETTINGS["comfort_setpoint"], 20)
            building.set_setpoint(SETTINGS["comfort_setpoint"])
            setpoints.append(SETTINGS["comfort_setpoint"])
        else:
            optimal_setpoint = building.get_next_setpoint(ot, SETTINGS["comfort_setpoint"], free_time)
            if optimal_setpoint < SETTINGS["setback_setpoint"]:
                optimal_setpoint = SETTINGS["setback_setpoint"]
            building.set_setpoint(optimal_setpoint)
            setpoints.append(optimal_setpoint)

    recorded_temperatures.append(str(building.get_temperature()))
    print(" ")
    now = now + datetime.timedelta(minutes=15)
    # Set up the next run

    if now.day == 2:
        # Simulation for one day is complete
        recorded_temperatures.append("21.0")
        with open('results/recorded_temps.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(recorded_temperatures)
        with open('results/setpoints.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(setpoints)
        with open('results/outdoor_temps.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(outdoor_temperatures)
        return 0
    sc.enter(60 * SETTINGS["time_interval"], 1, choose_setpoint,
             (building, weather_service, now, sc,))


if __name__ == "__main__":
    initialize_dbs()
    building = Building()
    weather_service = WeatherService()
    s = sched.scheduler(time.time, time.sleep)
    now = datetime.datetime(2015, 1, 1, 0, 0)
    s.enter(60 * SETTINGS["time_interval"], 1,
            choose_setpoint, (building, weather_service, now, s,))
    s.run()
