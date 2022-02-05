#!/usr/bin/env python3

from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarReader:
    def __init__(self):
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        creds = None
        if os.path.exists('../credentials/calendar_token.json'):
            creds = Credentials.from_authorized_user_file('../credentials/calendar_token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'daily_update_key.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('../credentials/calendar_token.json', 'w') as token:
                token.write(creds.to_json())
        self.creds = creds

    def get_events(self):
        try:
            service = build('calendar', 'v3', credentials=self.creds)
            # Call the Calendar API
            now = datetime.datetime.utcnow()
            time_max = now + datetime.timedelta(hours=24)
            now = now.isoformat() + "Z"
            time_max = time_max.isoformat() + "Z"
            events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=time_max,
                                                  maxResults=10,
                                                  singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])
        except HttpError as error:
            print('An error occurred: %s' % error)
            events = []
        return events


def main():
    calendar = CalendarReader()
    print(calendar.get_events())


if __name__ == '__main__':
    main()
