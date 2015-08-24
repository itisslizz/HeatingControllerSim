#!/usr/bin/env python3

# This file is part of the Python aiocoap library project.
#
# Copyright (c) 2012-2014 Maciej Wasilak <http://sixpinetrees.blogspot.com/>,
#               2013-2014 Christian Amsüss <c.amsuess@energyharvesting.at>
#
# aiocoap is free software, this file is published under the MIT license as
# described in the accompanying LICENSE file.

import logging

import asyncio

import aiocoap.resource as resource
import aiocoap
from math import exp

SETPOINT = 21.0
RC = 90000
MAX_R_E_in = 40.5


class TemperatureResource(resource.Resource):

    def __init__(self):
        super(TemperatureResource, self).__init__()
        """TO USE WITH PRERECORDED TEMPERATURES"""
        self.prerecorded = False
        if self.prerecorded:
            # Read in the recorded Temperatures
            with open('sim_data/weather_sim2') as f:
                self.temperatures = f.readlines()
        else:
            # Read in the outdoor Temperatures
            with open('sim_data/weather_sim2') as f:
                self.o_temperatures = f.readlines()
            # Set initial temperature
            self.current_temp = 21.0
        self.index = 0
        self.heat_power = 0

    @asyncio.coroutine
    def render_get(self, request):
        if self.prerecorded:
            # Get the temperature from the initialized list
            temp = self.temperatures[self.index].strip()
            if self.index < len(self.temperatures) - 1:
                self.index = self.index + 1

        else:
            # Calculate next temperature with the model
            temp = self.calc_next_temp()
            self.current_temp = temp
            if self.index < len(self.o_temperatures) - 1:
                self.index = self.index + 1
        response = aiocoap.Message(code=aiocoap.CONTENT,
                                   payload=(str(temp)).encode('utf8'))

        return response

    def calc_next_temp(self):
        if SETPOINT < self.current_temp:
            R_E_in = 0
        else:
            R_E_in = MAX_R_E_in
        next_temp = self.current_temp * exp(-900.0/RC) + (R_E_in + float(self.o_temperatures[self.index])) * (1 - exp(-900.0/RC))
        if R_E_in > 0:
            if next_temp > SETPOINT:
                next_temp = SETPOINT
        else:
            if next_temp < SETPOINT:
                next_temp = SETPOINT
        current_heat_power = ((next_temp - self.current_temp * exp(-900.0/RC)) / (1-exp(-900.0/RC)) - float(self.o_temperatures[self.index])) / 0.005
        print ("Effective Heat Power: ", current_heat_power)
        self.heat_power = self.heat_power + current_heat_power
        print ("Total Effective Heat Power: ", self.heat_power)
        return next_temp


class SetpointResource(resource.Resource):

    def __init__(self):
        super(SetpointResource, self).__init__()
        self.setpoint = str(SETPOINT).encode('utf8')

    @asyncio.coroutine
    def render_get(self, request):
        response = aiocoap.Message(code=aiocoap.CONTENT,
                                   payload=(self.setpoint))
        return response

    @asyncio.coroutine
    def render_put(self, request):
        print('PUT payload: %s' % request.payload)
        self.setpoint = request.payload
        global SETPOINT
        SETPOINT = float(self.setpoint)
        payload = ("New setpoint has been accepted and set to:"
                   "\n\n%r" % self.setpoint).encode('utf8')
        return aiocoap.Message(code=aiocoap.CHANGED, payload=payload)

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.INFO)


def main():
    # Resource tree creation
    root = resource.Site()

    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))

    root.add_resource(('temperature',), TemperatureResource())

    root.add_resource(('setpoint',), SetpointResource())

    asyncio.async(aiocoap.Context.create_server_context(root))

    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
