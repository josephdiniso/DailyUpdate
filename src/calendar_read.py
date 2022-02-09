#!/usr/bin/env python3

from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore


class CalendarReader:
    def __init__(self):
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        creds = None

        directory = os.path.dirname(__file__)
        credential_dir = os.path.join(directory, "../credentials/calendar_token.json")
        oauth_key_dir = os.path.join(directory, "../credentials/calendar_credentials.json")
        if os.path.exists(credential_dir):
            creds = Credentials.from_authorized_user_file(credential_dir, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    oauth_key_dir, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(credential_dir, 'w') as token:
                token.write(creds.to_json())
        self.creds = creds

    def get_events(self):
        try:
            service = build('calendar', 'v3', credentials=self.creds)
            # Call the Calendar API
            now = datetime.datetime.utcnow()
            time_max = now + datetime.timedelta(hours=16)
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
