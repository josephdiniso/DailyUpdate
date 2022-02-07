#!/usr/bin/env python3

from __future__ import print_function
from datetime import datetime
from typing import List, Any, Optional

import os.path

from google.auth.transport.requests import Request  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore


class SheetsReader:
    def __init__(self, spreadsheet_id: str, range: str):
        self.spreadsheet_id = spreadsheet_id
        self.range = range
        self._authenticate()

    def get_workout(self) -> List:
        """
        Returns parsed workout data from the specified Google Sheet

        Returns:
            List of Lists containing string values for the cells
        """
        values = self._get_data()
        return self._parse_data(values)

    def _authenticate(self) -> None:
        """
        Sets the credentials for the session
        """
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = None
        directory = os.path.dirname(__file__)
        credential_dir = os.path.join(directory, "../credentials/token.json")
        oauth_key_dir = os.path.join(directory,
                                     "../credentials/drive_credentials.json")
        if os.path.exists(credential_dir):
            creds = Credentials.from_authorized_user_file(credential_dir,
                                                          SCOPES)
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

    def _get_data(self) -> Optional[Any]:
        """
        Pulls data from range of Google Sheet

        Returns
            List of data entries
        """
        values = None
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                        range=self.range).execute()
            values = result.get('values', [])
        except HttpError as err:
            print(err)
        return values

    def _parse_data(self, values) -> List:
        """
        Parses entire sheet and creates a list of lists of the relevant boxes

        Params:
            values: raw Sheets data

        Returns:
            formatted Sheets data
        """
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
    def _check_ending(row: List) -> bool:
        """
        Finds where a grouping ends by seeing the next cell that contains a
        day of the week

        Fairly primitive way of going about it, but it's the only way that
        avoids explicitly adding a
        break in the Google Sheet.

        params:
            row: Row in the spreadsheet

        Returns:
            True if no day is in the row, False if there is a day in the cell
        """
        week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                "Saturday", "Sunday"]
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
