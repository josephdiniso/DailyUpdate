import requests
import json
import time
from dataclasses import dataclass
import datetime
from typing import Union, List, Tuple


@dataclass
class Location:
    def __init__(self, city: str, state: str, country: str):
        self.city = city
        self.state = state
        self.country = country


@dataclass
class WeatherChars:
    def __init__(self, min_temp: bool = True, max_temp: bool = True, pressure: bool = False, humidity: bool = False,
                 weather: bool = True, wind_speed: bool = False):
        self._enable_min_temp: bool = min_temp
        self._enable_max_temp: bool = max_temp
        self._enable_pressure: bool = pressure
        self._enable_humidity: bool = humidity
        self._enable_weather: bool = weather
        self._enable_wind_speed: bool = wind_speed

        self._min_temp: float = 0
        self._max_temp: float = 0
        self._pressure: float = 0
        self._humidity: float = 0
        self._weathers: List[Tuple[str, str]] = []
        self._wind_speed: float = 0
        self._unix_times: List[float] = []

    def __repr__(self):
        return f"{self._min_temp=}, {self._max_temp=}, {self._pressure=}, {self._humidity=}, {self._weathers=}, {self._wind_speed=}, {self._unix_times=}"

    def __str__(self):
        return self.__repr__()

    @property
    def min_temp(self):
        return self._min_temp

    @min_temp.setter
    def min_temp(self, value):
        self._min_temp = value

    @property
    def max_temp(self):
        return self._max_temp

    @max_temp.setter
    def max_temp(self, value):
        self._max_temp = value

    @property
    def pressure(self):
        return self.pressure

    @pressure.setter
    def pressure(self, value):
        self._pressure = value

    @property
    def humidity(self):
        return self._humidity

    @humidity.setter
    def humidity(self, value):
        self._humidity = value

    @property
    def weathers(self):
        return self._weathers

    @weathers.setter
    def weathers(self, value):
        self._weathers = value

    @property
    def wind_speed(self):
        return self._wind_speed

    @wind_speed.setter
    def wind_speed(self, value):
        self._wind_speed = value

    @property
    def unix_times(self):
        return self._unix_times

    @unix_times.setter
    def unix_times(self, value):
        self._unix_times = value


class Weather:
    def __init__(self, api_path: str, location: Location, weather_chars: WeatherChars, units: str = "imperial"):
        with open(api_path, "r") as f:
            self.api_key = f.read().splitlines()[0]
        self.location = location
        self.weather_chars = weather_chars
        self.units = units
        # self._weather_json = self._get_weather()
        self._weather_json = self._get_local_weather()
        self._get_forecast()
        self._datetimes = self._convert_datetimes(self.weather_chars.unix_times)

    # TODO: Adjust for custom time zones
    @staticmethod
    def _convert_datetimes(unix_times: List[float]):
        return [datetime.datetime.fromtimestamp(unix_time, datetime.timezone(datetime.timedelta(hours=-5))) for
                unix_time in unix_times]

    @staticmethod
    def _get_local_weather():
        with open("test.json", "r") as f:
            text = f.read()
        new_obj = json.loads(text)
        return new_obj

    def _get_weather(self):
        q_val = f"{self.location.city},{self.location.state},{self.location.country}"
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast?q={q_val}&appid={self.api_key}&units={self.units}")
        return json.loads(response.text)

    def _get_forecast(self):
        current_time = time.time()
        weather_counts = 0
        maxes = []
        mins = []
        pressures = []
        humidities = []
        wind_speeds = []
        weathers = []
        unix_times = []
        for weather_report in self._weather_json["list"]:
            if weather_report["dt"] < current_time:
                continue
            if weather_report["dt"] > current_time + (86400 // 2):
                break
            weather_counts += 1
            pressures.append(weather_report["main"]["pressure"])
            humidities.append(weather_report["main"]["humidity"])
            wind_speeds.append(weather_report["wind"]["speed"])
            weathers.append((weather_report["weather"][0]["main"], weather_report["weather"][0]["description"]))
            mins.append(weather_report["main"]["temp_min"])
            maxes.append(weather_report["main"]["temp_max"])
            unix_times.append(weather_report["dt"])

        self.weather_chars.min_temp = min(mins)
        self.weather_chars.max_temp = max(maxes)
        self.weather_chars.pressure = sum(pressures) / weather_counts
        self.weather_chars.humidity = sum(humidities) / weather_counts
        self.weather_chars.wind_speed = sum(wind_speeds) / weather_counts
        self.weather_chars.weathers = weathers
        self.weather_chars.unix_times = unix_times


def main():
    city = "Blacksburg"
    state = "VA"
    country = "USA"
    units = "imperial"
    api_path = "api_key"
    location = Location(city, state, country)
    weatherChars = WeatherChars()
    weather = Weather(api_path, location, weatherChars, units=units)


if __name__ == "__main__":
    main()
