#!/usr/bin/env python3

from __future__ import print_function
from datetime import datetime
from typing import List

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SheetsReader:
    def __init__(self, spreadsheet_id: str, range: str):
        self.spreadsheet_id = spreadsheet_id
        self.range = range
        self.creds = self._authenticate()

    def get_workout(self):
        values = self._get_data()
        return self._parse_data(values)

    # TODO: Add authentication check
    @staticmethod
    def _authenticate():
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = None
        if os.path.exists('../credentials/token.json'):
            creds = Credentials.from_authorized_user_file('../credentials/token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '../credentials/drive_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('../credentials/token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def _get_data(self):
        values = None
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                        range=self.range).execute()
            values = result.get('values', [])
            if not values:
                print('No data found.')
                return []
        except HttpError as err:
            print(err)
        return values

    def _parse_data(self, values):
        full_date = datetime.now().strftime("%A %-m/%-d/%y")
        printing = False
        output = []
        for row in values:
            if not self._check_ending(row) and printing:
                break
            if full_date in row:
                printing = True
            if printing:
                if row:
                    output.append(row)
        return output

    @staticmethod
    def _check_ending(row: List):
        week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for cell in row:
            for day in week:
                if day in cell:
                    return False
        return True


def main():
    id = '1NrQq5ARs_b1G0Zb_uinnvGkdIjqUHRoDcUOHtLaVl0A'
    current_month = datetime.now().strftime("%B")
    range = f"{current_month}!A1:F10" \
            f"000"
    reader = SheetsReader(id, range)
    print(reader.get_workout())


if __name__ == '__main__':
    main()
