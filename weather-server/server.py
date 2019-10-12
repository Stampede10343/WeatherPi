from flask import Flask
from flask import request, jsonify, render_template, make_response

import os.path
import time
from datetime import datetime

import sqlite3

import numpy as np
from scipy import signal

PRETTY_DATE = '%b, %d %I:%M %p'

app = Flask(__name__)

@app.route('/temperature', methods=['POST'])
def log_temperatue():
    if request.json:
        print(request.json)

        connection = get_connection()
        connection.execute('''INSERT INTO temperature VALUES (?, ?)''', (time.time(), request.json['temp']))
        connection.commit()
        connection.close()
    else:
        print('No json: ', request)

    return jsonify({"status": "success"})

@app.route('/temperature', methods=['GET'])
def get_temperature():
    unit = request.cookies.get('unit', 'C')
    unit = request.args.get('unit', unit)
    unit = 'C' if unit != 'F' else unit

    connection = get_connection()
    temps = []
    for temp_reading in connection.execute('''SELECT date as d, temp FROM temperature WHERE d >= strftime('%s', 'now', '-1 day') ORDER BY d;'''):
        temp = temp_reading[1]
        temp = temp if unit == 'C' else (temp * 1.8) + 32
        temp_reading = (temp_reading[0], temp)
        temps.append(temp_reading)

    maxt, max_time = connection.execute('''SELECT MAX(temp), date FROM temperature WHERE date > strftime('%s', 'now', '-1 day')''').fetchone()
    mint, min_time = connection.execute('''SELECT MIN(temp), date FROM temperature WHERE date > strftime('%s', 'now', '-1 day')''').fetchone()
    connection.close()

    maxt = convert_temp(maxt, unit)
    mint = convert_temp(mint, unit)
    max_temp = str(round(maxt, 1)) + ' ' + unit
    max_time = datetime.fromtimestamp(max_time).strftime(PRETTY_DATE)
    min_temp = str(round(mint, 1)) + ' ' + unit
    min_time = datetime.fromtimestamp(min_time).strftime(PRETTY_DATE)

    filtered_temps = []
    interval = request.cookies.get('interval', 15)
    batch = int(request.args.get('interval', interval))

    for index in range(batch, len(temps), batch):
        average_temp = 0
        average_time = 0
        for i in range(index - batch, index):
            average_time = average_time + temps[index][0]
            average_temp = average_temp + temps[index][1]

        filtered_temps.append((average_time/batch, average_temp/batch))

    data = {
        'labels': [],
        'datasets': [
            {
                'label': 'Temperature',
                'data': [],
                'backgroundColor': 'rgba(10, 50, 190, 0.3)'
            }
        ]
    }

    for temp_reading in filtered_temps:
        data['labels'].append(datetime.fromtimestamp(temp_reading[0]).strftime('%b, %d %I:%M %p'))
        data['datasets'][0]['data'].append(temp_reading[1])

    response = make_response(render_template('dashboard.html',
                           data=data, unit=unit, max_temp=max_temp, min_temp=min_temp, max_time=max_time, min_time=min_time))
    response.set_cookie('unit', unit)
    response.set_cookie('interval', str(batch))

    return response
def convert_temp(temp, unit):
    return temp if unit == 'C' else (temp * 1.8) + 32


@app.route('/sampled')
def get_sampled_data():
    unit = request.args.get('unit', 'C')
    unit = 'C' if unit != 'F' else unit

    connection = get_connection()
    temps = []
    for temp_reading in connection.execute('''SELECT date, temp FROM temperature ORDER BY date'''):
        temp = temp_reading[1]
        temp = temp if unit == 'C' else (temp * 1.8) + 32
        temp_reading = (temp_reading[0], temp)
        temps.append(temp_reading)

    connection.close()

    datapoints = 100
    filtered_temps = []
    while len(temps) % datapoints != 0:
        temps.append((None, None))


    array = np.array(temps).reshape(-1, 2).reshape(-1, datapoints)
    # array = array.reshape(-1, datapoints).mean(axis=1)

    return jsonify({'shape': len(array.shape), 'all':array.size, 'yee': str(array)})

def get_connection():
    return sqlite3.connect('temperature.db')

if __name__ == "__main__":
    if not os.path.isfile('temperature.db'):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE temperature (date INTEGER, temp REAL)''')
        connection.commit()
        connection.close()

    app.run(host='0.0.0.0', port=8888, debug=True)
