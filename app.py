from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from future.standard_library import import install_aliases
install_aliases()

from urllib.parse import import urlparse, urlencode
from urllib.request import import urlopen, Request
from urllib.error import import HTTPError

import json
import os

from flask import import Flask
from flask import import request
from flask import import make_response

import datetime

app = Flask(__name__)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    home_dir = os.path.expanduser('~')
    print(home_dir)
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def create_event(date,start_time,end_time):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    summary = "Summary"
    description = "Description goes here"
    GMT_OFF = '+05:30'
    start_time = date + 'T' + start_time + GMT_OFF
    end_time = date + 'T' + end_time + GMT_OFF
    EVENT = {
        'summary' : summary,
        'start' : {'dateTime' : start_time},
        'end' : {'dateTime' : end_time},
    }
    e = service.events().insert(calendarId = 'primary',
                                sendNotifications=True, body=EVENT).execute()
    print ("Event added")


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    if req.get("result").get("action") != "createEvent":
        return {}
    parameters = req.get('result').get('parameters')
    if parameters is None:
        return {}

    date = parameters.get('date')
    if date is None:
        return{}

    start_time = parameters.get('start_time')
    if start_time is None:
        return {}

    end_time = result.get('channel')
    if end_time is None:
        return {}

    create_event(date,start_time,end_time)
    res = makeWebhookResult(date,start_time,end_time)

    return res

def makeWebhookResult(date,start_time,end_time):
    speech = "Event booked on " + date +" at "+ start_time + " until " + end_time

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "app.py"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
