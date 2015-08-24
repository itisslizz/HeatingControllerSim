"""
This module will provide weather information
"""


class WeatherService:
    def __init__(self):
        self.location = 'Baden,ch'
        with open('sim_data/weather_sim2') as f:
            self.temperatures = f.readlines()
        self.index = 0

    def get_current_temperature(self):
        temp = self.temperatures[self.index]
        self.index = self.index + 1
        if self.index == len(self.temperatures):
            self.index = self.index - 1
        return float(temp)
