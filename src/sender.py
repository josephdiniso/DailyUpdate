#!/usr/bin/env python3

import os
import datetime
import calendar

from sendgrid import SendGridAPIClient  # type: ignore
from sendgrid.helpers.mail import Mail  # type: ignore


class DateUtil:
    def __init__(self):
        pass

    @staticmethod
    def _get_today():
        today = datetime.date.today()
        return {"day": calendar.day_name[today.weekday()],
                "date": today.day,
                "month": calendar.month_name[today.month],
                "year": today.year}

    def formatted_date(self):
        today = self._get_today()
        subject = f"{today['day']}, {today['month'][:3]} {today['date']}, {str(today['year'])[-2:]}"
        return subject


class Sender:
    def __init__(self, sender: str):
        self.date_util = DateUtil()
        self.sender = sender

    def send_mail(self, destination, content=None, subject=None):
        if not content:
            with open("index.html", "r") as f:
                content = f.read()
        if not subject:
            subject = f"Daily Report: {self.date_util.formatted_date()}"
        message = Mail(
            from_email=self.sender,
            to_emails=destination,
            subject=subject,
            html_content=content)
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)


def main():
    sender = Sender("josephdiniso@gmail.com")
    sender.send_mail("josephdiniso@vt.edu")


if __name__ == "__main__":
    main()
