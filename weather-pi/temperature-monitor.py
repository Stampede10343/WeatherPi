#!/usr/bin/env python

from envirophat import weather

import requests

import time

from subprocess import PIPE, Popen

def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

def adjust_temperature(sensor_temp):
    cpu_temp_c = get_cpu_temperature()
    temp_c_cal = sensor_temp - ((cpu_temp_c-sensor_temp)/1.3)

    return temp_c_cal

weather.altitude(qnh=1020)

while True:
    temp = weather.temperature()
    temp = adjust_temperature(temp)

    pressure = weather.pressure(unit='hPa')
    print(temp, pressure)
    req = requests.post('http://192.168.1.23:8888/temperature', json={'temp':temp, 'pressure': pressure})
    print('status:', req.status_code)

    time.sleep(60)
