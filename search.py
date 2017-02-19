#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "GoogleSearch":
        return {}
    baseurl = "https://www.googleapis.com/customsearch/v1?"
	KEY = "AIzaSyDNYsLn4JGIR4UaZMFTAgDB9gKN3rty2aM"
	CSE = "003066316917117435589%3Avcms6hy5lxs"
	google_query = makeSearchQuery(req)
    if google_query is None:
        return {}
    google_query = baseurl + KEY + "&cx=" + CSE + "&q=" + search_string + "&num=1"
    result = urllib.request.urlopen(google_query).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeSearchQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    search_string = parameters.get("any")
    if search_string is None:
        return None

    return baseurl + KEY + "&cx=" + CSE + "&q=" + search_string + "&num=1"


def makeWebhookResult(data):
    parsed_input = data.get('query')
    if parsed_input is None:
        return {}

    items = parsed_input.get['items']
    if items is None:
        return {}
		
	
    speech = items.get('snippet')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
