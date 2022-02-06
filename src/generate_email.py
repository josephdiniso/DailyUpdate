#!/usr/bin/env python3
from datetime import datetime
from typing import Optional
from typing import List
from typing import Dict
from typing import Tuple
from dateutil import parser
import os

import bs4

from sheets_read import SheetsReader
from weather import Location, WeatherChars, Weather
from calendar_read import CalendarReader
from sender import Sender


class Generator:
    def __init__(self):
        self.workout: Optional[List[List[str]]] = None
        self.calendar: Optional[List[Dict[str, str]]] = None
        self.weather: Optional[List] = None

    def get_sheets(self, id: str, range: str) -> None:
        """
        Calls Sheets API and gets workout values

        params:
            id: ID of Sheets file
            range: Range of values to grab from Sheets file
        """
        reader = SheetsReader(id, range)
        self.workout = reader.get_workout()

    def get_calendar(self) -> None:
        """
        Calls calendar API and gets calendar values
        """
        calendar = CalendarReader()
        self.calendar = calendar.get_events()

    def get_weather(self, api_path: str, location: Location, units: Optional[str] = None) -> None:
        """
        Calls weather API and gets weather values

        Params:
            api_path: path to OpenWeather API key
            location: Location object with location of user
            units: Custom units, defaults to imperial
        """
        weather_chars = WeatherChars()
        if units is not None:
            weather = Weather(api_path, location, weather_chars=weather_chars, units=units)
        else:
            weather = Weather(api_path, location, weather_chars=weather_chars)
        self.weather = weather.weather_chars

    def read_template(self, file_name: str) -> str:
        """
        Reads a template index.html stored locally and modifies it with custom
        output

        Params:
            file_name: Path of templatr html file

        Returns:
            Modified html as a string
        """
        with open(file_name) as f:
            txt = f.read()
            soup = bs4.BeautifulSoup(txt, "html.parser")

        self._generate_table(soup)
        self._generate_calendar(soup)
        self._generate_weather(soup)
        return str(soup)

    @staticmethod
    def send_email(destination: str, content: str, subject: Optional[str] = None) -> None:
        """
        Sends an email to a desired user, calling the Sender object

        Params:
            destination: Destination email address
            content: Email content
            subject: Email subject, if not set will default to a pre-defined string
        """
        sender = Sender("josephdiniso@gmail.com")
        if subject:
            sender.send_mail(destination, content, subject=subject)
        else:
            sender.send_mail(destination, content)

    def _generate_weather(self, soup: bs4.BeautifulSoup) -> None:
        """
        Modifies HTML template with updated weather values

        Params:
            soup: BeautifulSoup object containing output HTML
        """
        low_temp = soup.find_all(tag="low-temp")
        low_temp[0].string = f"{self.weather.min_temp} °F"

        high_temp = soup.find_all(tag="high-temp")
        high_temp[0].string = f"{self.weather.max_temp} °F"

        pressure = soup.find_all(tag="pressure")
        pressure[0].string = f"{self.weather.pressure} hPa"

        humidity = soup.find_all(tag="humidity")
        humidity[0].string = f"{self.weather.humidity}%"

        wind_speed = soup.find_all(tag="wind-speed")
        wind_speed[0].string = f"{self.weather.wind_speed:.1f} mph"

        periods, normal_times = self._convert_times(self.weather.unix_times)
        weather_times = soup.find_all(class_="weather-time")
        weather_note = soup.find_all(class_="weather-note")
        weather_temp = soup.find_all(class_="weather-temp")

        assert len(weather_times) == len(weather_note) == len(weather_temp)
        for index in range(len(weather_times)):
            if index > 2:
                break
            if periods[index] == periods[index + 1]:
                weather_times[
                    index].string = f"{normal_times[index]} - {normal_times[index + 1]}{periods[index + 1][0]}"
            else:
                weather_times[
                    index].string = f"{normal_times[index]}{periods[index][0]} - {normal_times[index + 1]}{periods[index + 1][0]}"
            weather_note[index].string = f"{self.weather.weathers[index][0]}"
            weather_temp[index].string = f"{self.weather.feels_like[index]} °F"

    @staticmethod
    def _convert_times(unix_times: List[int]) -> Tuple[List[str], List[str]]:
        """
        Takes a list of unix times and converts them to their periods and 12 hour times
        Params:
            unix_times: List of unix times in seconds

        Returns:
            periods (either AM or PM) for each unix time
            times converted to 12-hour time
        """
        full_times = [datetime.fromtimestamp(unix_time).strftime("%-I") for unix_time in unix_times]
        periods = [datetime.fromtimestamp(unix_time).strftime("%p") for unix_time in unix_times]
        return periods, full_times

    def _generate_calendar(self, soup: bs4.BeautifulSoup):
        """
        Modifies HTML template with updated calendar values

        Params:
            soup: BeautifulSoup object containing output HTML
        """
        schedule_list = soup.find_all(tag="schedule-list")
        if not self.calendar:
            div = soup.new_tag("div", class_="event")
            p = soup.new_tag("p", class_="event-name")
            p.string = "No events today, enjoy!"
            div.append(p)
            schedule_list[0].append(div)
            return

        for event in self.calendar:
            div = soup.new_tag("div", class_="event")
            li = soup.new_tag("li")
            event_title = soup.new_tag("p", class_="event-name")
            event_title.string = event["summary"]
            event_info = soup.new_tag("p", class_="event-info")

            start_val = event.get("start", None)
            if start_val:
                start_val = start_val.get("dateTime", None)
            end_val = event.get("end", None)
            if end_val:
                end_val = end_val.get("dateTime", None)
            all_day = False
            if start_val and end_val:
                start_time = parser.parse(start_val)
                start_time = start_time.strftime("%H:%M")
                end_time = parser.parse(end_val)
                end_time = end_time.strftime("%H:%M")
            else:
                all_day = True
            location = event.get("location", "")
            if all_day:
                output = f"All Day"
            else:
                output = f"{start_time} - {end_time}"
            if location:
                output += f", {location}"

            event_info.string = output
            li.append(event_title)
            li.append(event_info)
            div.append(li)
            schedule_list[0].append(div)

    def _generate_table(self, soup: bs4.BeautifulSoup):
        """
        Params:
            soup: BeautifulSoup object containing output HTML
        """
        if not self.workout:
            prompt = soup.find_all(tag="workout-prompt")
            prompt[0].string = "No workout today, have fun!"

        table = soup.new_tag("table")
        max_width = 0
        for row in self.workout:
            if len(row) > max_width:
                max_width = len(row)

        for row in self.workout:
            tr = soup.new_tag("tr")
            for col in row:
                td = soup.new_tag("td")
                td.string = col
                tr.append(td)
            if len(row) < max_width:
                for _ in range(max_width - len(row)):
                    td = soup.new_tag("td")
                    tr.append(td)
            table.append(tr)
        workout_tag = soup.find_all(tag="workout-container")
        workout_tag[0].append(table)

    def __repr__(self):
        print(f"{self.workout=}, {self.calendar=}, {self.weather=}")


def main():
    directory = os.path.dirname(__file__)
    generator = Generator()
    id = '1NrQq5ARs_b1G0Zb_uinnvGkdIjqUHRoDcUOHtLaVl0A'
    current_month = datetime.now().strftime("%B")
    range = f"{current_month}!A1:F10000"
    generator.get_sheets(id, range)
    city = "Blacksburg"
    state = "VA"
    country = "USA"
    units = "imperial"
    api_path = os.path.join(directory, "../credentials/api_key")
    location = Location(city, state, country)
    generator.get_weather(api_path, location, units=units)
    generator.get_calendar()

    content = generator.read_template(os.path.join(directory, "template/index.html"))
    generator.send_email("josephdiniso@vt.edu", content)


if __name__ == "__main__":
    main()
