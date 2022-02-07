import requests  # type: ignore
import json
import time
from dataclasses import dataclass
import datetime
from typing import List, Any
from typing import Tuple


@dataclass
class Location:
    """
    Dataclass to store location attributes
    """

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

        self.min_temp: float = 0
        self.max_temp: float = 0
        self.pressure: float = 0
        self.humidity: float = 0
        self.weathers: List[Tuple[str, str]] = []
        self.wind_speed: float = 0
        self.unix_times: List[float] = []
        self.feels_like: List[float] = []

    def __repr__(self):
        return f"{self.min_temp=}, {self.max_temp=}, {self.pressure=}, {self.humidity=}, {self.weathers=}, {self.wind_speed=}, {self.unix_times=}"

    def __str__(self):
        return self.__repr__()


class Weather:
    def __init__(self, api_path: str, location: Location, weather_chars: WeatherChars = WeatherChars(),
                 units: str = "imperial"):
        with open(api_path, "r") as f:
            self.api_key = f.read().splitlines()[0]
        self.location = location
        self._weather_chars = weather_chars
        self.units = units
        self._weather_json = self._get_weather()
        # self._weather_json = self._get_local_weather()
        self._get_forecast()
        self._datetimes = self._convert_datetimes(self.weather_chars.unix_times)

    @property
    def weather_chars(self):
        return self._weather_chars

    # TODO: Adjust for custom time zones
    @staticmethod
    def _convert_datetimes(unix_times: List[float], time_difference: int = -5) -> List[datetime.datetime]:
        """
        Converts unix times to datetime objects

        Params:
            unix_times: List of unix times in seconds
        """
        return [datetime.datetime.fromtimestamp(unix_time, datetime.timezone(datetime.timedelta(hours=time_difference)))
                for
                unix_time in unix_times]

    @staticmethod
    def _get_local_weather() -> Any:
        """
        Helper method to get a weather JSON saved locally

        Returns:
            JSON object of saved weather data
        """
        with open("test.json", "r") as f:
            text = f.read()
        new_obj = json.loads(text)
        return new_obj

    def _get_weather(self) -> Any:
        """
        Calls OpenWeather API and gets weather data

        Returns:
            JSON object of weather data
        """
        q_val = f"{self.location.city},{self.location.state},{self.location.country}"
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast?q={q_val}&appid={self.api_key}&units={self.units}")
        return json.loads(response.text)

    def _get_forecast(self) -> None:
        """
        Populates WeatherChars object with weather data for consumption
        """
        current_time = time.time()
        weather_counts = 0
        maxes = []
        mins = []
        pressures = []
        humidities = []
        wind_speeds = []
        weathers = []
        unix_times = []
        feels_like = []
        if not self._weather_json:
            return
        for weather_report in self._weather_json["list"]:
            if weather_report["dt"] < current_time:
                continue
            SECONDS_IN_DAY = 86400
            if weather_report["dt"] > current_time + (SECONDS_IN_DAY // 2):
                break
            weather_counts += 1
            pressures.append(weather_report["main"]["pressure"])
            humidities.append(weather_report["main"]["humidity"])
            wind_speeds.append(weather_report["wind"]["speed"])
            weathers.append((weather_report["weather"][0]["main"], weather_report["weather"][0]["description"]))
            mins.append(weather_report["main"]["temp_min"])
            maxes.append(weather_report["main"]["temp_max"])
            unix_times.append(weather_report["dt"])
            feels_like.append(weather_report["main"]["feels_like"])

        self.weather_chars.min_temp = min(mins)
        self.weather_chars.max_temp = max(maxes)
        self.weather_chars.pressure = sum(pressures) / weather_counts
        self.weather_chars.humidity = sum(humidities) / weather_counts
        self.weather_chars.wind_speed = sum(wind_speeds) / weather_counts
        self.weather_chars.weathers = weathers
        self.weather_chars.unix_times = unix_times
        self.weather_chars.feels_like = feels_like


def main():
    city = "Blacksburg"
    state = "VA"
    country = "USA"
    units = "imperial"
    api_path = "../credentials/api_key"
    location = Location(city, state, country)
    weatherChars = WeatherChars()
    weather = Weather(api_path, location, weatherChars, units=units)
    print(weather.weather_chars)


if __name__ == "__main__":
    main()
