# WeatherPi
A simple weather information collecting application built using Python, a RaspberryPi and EnviroPhat.

# Requirements
- Python 2/3
- Flask

# Setup
See [link](https://github.com/pimoroni/enviro-phat) for enviro-phat download/setup.
Configure `weather-server/server.py` to run with desired port `8888` by default.
Configure `weather-pi/temperature-monitor.py` to match the server config.

# Run
- Run `python weather-pi/server.py` to start server
- Run `python temperature-monitor.py` on the RaspberryPi
