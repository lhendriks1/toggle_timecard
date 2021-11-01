#!/usr/bin/env python3
from urllib import request, error
from base64 import b64encode
from datetime import datetime, timedelta
from calendar import monthrange
from json import dumps
from time import sleep

def _daterange(start, end):
    for n in range(int((end - start).days)):
        yield start + timedelta(n)


def _createEntry(date):
    return {
        "time_entry":
            {
                "start": date, # time entry start time (string, required, ISO 8601 date and time)
                "duration": 28800,  # time entry duration in seconds
                "pid": 175174979,  # project ID (integer, not required)
                "wid": 945833,  # workspace ID (integer, required if pid or tid not supplied)
                "billable": True, # (boolean, not required, default false, available for pro workspaces)
                "created_with": "python script",
                #  "tags": '', (array of strings, not required)
                #  "description: '' string, not required
            }
    }


def _getMonthDates():
    today = datetime.today()
    lastDay = today.replace(day=monthrange(today.year, today.month)[1])
    firstDay = today.replace(day=1)

    dates = []
    for single_date in _daterange(firstDay, lastDay + timedelta(days=1)):
        if single_date.isoweekday() in range(1, 6):
            dates.append(single_date.strftime("%Y-%m-%dT09:00:00-04:00"))

    return dates


def _postEntry(auth_header, entry):
    path = 'https://api.track.toggl.com/api/v8/time_entries'
    body = dumps(entry).encode()
    headers = {
        'Content-type': 'application/json',
        'Authorization': auth_header
    }


    try:
        req = request.Request(path, body, headers)
        with request.urlopen(req) as response:
            print('success: ' + response.read().decode())
    except error.HTTPError as httpError:
        e = httpError.read().decode()
        print('error: ' + e)


def _getAuth():
    token = input('Enter your Toggl token:')
    base64_bytes = b64encode(f'{token}:api_token'.encode()).decode('utf8')
    return f'Basic {base64_bytes}'


def main():
    use_current_month = input(f'Do you want to fill out your toggl timecard for the entire month of {datetime.now().strftime("%B")}? (y/n) ')
    if use_current_month == 'n':
        print('Well that\'s too bad ... we don\'t support anything else rn')
        quit()

    auth_header = _getAuth()

    entries = []
    if use_current_month == 'y':
        for date in _getMonthDates():
            entries.append(_createEntry(date))
    else:
        quit()
        # TODO

    for entry in entries:
        _postEntry(auth_header, entry)
        # toggl api rate limits to approx 1 req per second, but a delay of .5s seems to work fine
        sleep(0.5)


if __name__ == "__main__":
    main()
