from flask import Flask
from flask import request, jsonify, render_template

import os.path
import time
from datetime import datetime

import sqlite3

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
    unit = request.args.get('unit', 'C')
    unit = 'C' if unit != 'F' else unit

    connection = get_connection()
    temps = []
    for temp_reading in connection.execute('''SELECT date, temp FROM temperature ORDER BY date'''):
        temp = temp_reading[1]
        temp = temp if unit == 'C' else (temp * 1.8) + 32
        temp_reading = (temp_reading[0], temp)
        temps.append(temp_reading)
        print(temp_reading)

    connection.close()

    data = {
        'labels': [],
        'datasets': [
            {
                'label': 'Temperature',
                'data': [],
                'backgroundColor': 'rgba(10, 50, 190, 0.2)'
            }
        ]
    }
    for temp_reading in temps:
        data['labels'].append(datetime.fromtimestamp(temp_reading[0]).strftime('%b, %d %I:%M %p'))
        data['datasets'][0]['data'].append(temp_reading[1])

    return render_template('dashboard.html', data=data, unit=unit)

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
