#!/usr/bin/env python3
from datetime import datetime
from typing import Optional, List, Dict

import bs4

from sheets_read import SheetsReader
from weather import Location, WeatherChars, Weather
from calendar_read import CalendarReader


class Generator:
    def __init__(self):
        self.workout: Optional[List[List[str]]] = None
        self.calendar: Optional[List[Dict[str, str]]] = None
        self.weather: Optional[List] = None

    def get_sheets(self, id, range):
        reader = SheetsReader(id, range)
        self.workout = reader.get_workout()

    def get_calendar(self):
        calendar = CalendarReader()
        self.calendar = calendar.get_events()

    def get_weather(self, api_path: str, location: str, weather_chars: str = None, units=None):
        if weather_chars is None:
            weather_chars = WeatherChars()
        if units is not None:
            weather = Weather(api_path, location, weather_chars=weather_chars, units=units)
        else:
            weather = Weather(api_path, location, weather_chars=weather_chars)
        self.weather = weather.weather_chars

    def read_template(self, file_name: str):
        print(self.workout)
        with open(file_name) as f:
            txt = f.read()
            soup = bs4.BeautifulSoup(txt, "html.parser")
        workout_tag = soup.find_all(tag="workout-container")
        print(workout_tag)

    def __repr__(self):
        print(f"{self.workout=}, {self.calendar=}, {self.weather=}")


def main():
    generator = Generator()
    id = '1NrQq5ARs_b1G0Zb_uinnvGkdIjqUHRoDcUOHtLaVl0A'
    current_month = datetime.now().strftime("%B")
    range = f"{current_month}!A1:F10000"
    generator.get_sheets(id, range)
    city = "Blacksburg"
    state = "VA"
    country = "USA"
    units = "imperial"
    api_path = "../credentials/api_key"
    location = Location(city, state, country)
    generator.get_weather(api_path, location, units=units)
    generator.get_calendar()

    generator.read_template("index.html")



if __name__ == "__main__":
    main()
