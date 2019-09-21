#!/usr/bin/env python

from envirophat import weather

import requests

import time

weather.altitude(qnh=1020)
while True:
    temp = weather.temperature()
    pressure = weather.pressure(unit='hPa')
    print(temp, pressure)
    req = requests.post('http://192.168.1.23:8888/temperature', json={'temp':temp, 'pressure': pressure})
    print('status:', req.status_code)

    time.sleep(5)
