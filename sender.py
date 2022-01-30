import os
import datetime
import calendar

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class DateUtil:
    def _get_today(self):
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

    def send_mail(self):
        message = Mail(
            from_email=self.sender,
            to_emails='josephdiniso@vt.edu',
            subject=f"Daily Report: {self.date_util.formatted_date()}",
            html_content="<h1>Hello gents, just testing</h1>")
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)


sender = Sender("josephdiniso@gmail.com")
sender.send_mail()
