"""
This module will communicate with the
Honeywell Thermostats using coap
"""
import asyncio

from aiocoap import *


@asyncio.coroutine
def coap_get_temperature(future):
    protocol = yield from Context.create_client_context()
    request = Message(code=GET)
    request.set_request_uri('coap://localhost/temperature')
    try:
        response = yield from protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        future.set_result(response.payload)


@asyncio.coroutine
def coap_get_setpoint(future):
    protocol = yield from Context.create_client_context()
    request = Message(code=GET)
    request.set_request_uri('coap://localhost/setpoint')
    try:
        response = yield from protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        future.set_result(response.payload)


@asyncio.coroutine
def coap_put_setpoint(setpoint):

    context = yield from Context.create_client_context()

    payload = str(setpoint).encode('utf-8')
    request = Message(code=PUT, payload=payload)
    request.opt.uri_host = 'localhost'
    request.opt.uri_path = ("setpoint",)

    response = yield from context.request(request).response

    # print('Result: %s\n%r'%(response.code, response.payload))

def put_setpoint(setpoint):
    asyncio.get_event_loop().run_until_complete(coap_put_setpoint(setpoint))


def get_setpoint():
    loop = asyncio.get_event_loop()
    future = asyncio.Future()
    asyncio.async(coap_get_setpoint(future))
    loop.run_until_complete(future)
    return float(future.result().decode('utf8'))


def get_temperature():
    loop = asyncio.get_event_loop()
    future = asyncio.Future()
    asyncio.async(coap_get_temperature(future))
    loop.run_until_complete(future)
    return float(future.result().decode('utf8'))
