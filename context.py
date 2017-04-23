#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os

from flask import Flask
from flask import request, render_template
from flask import make_response


# Flask weather should start in global layout
context = Flask(__name__)


@context.route('/webhook', methods=['POST'])
def webhook():
    reqContext = request.get_json(silent=True, force=True)
    print(json.dumps(reqContext, indent=4))
    print(reqContext.get("result").get("action"))
    if reqContext.get("result").get("action") == "yahooWeatherForecast":
       return weatherhook()
    elif reqContext.get("result").get("action") == "GoogleSearch":
       print("Within ELIF block after search string validation as of GoogleSearch")
       return searchhook()
       print("Redirection to GoogleSearch")
    else:
       print("Good Bye")


def weatherhook():
    req = request.get_json(silent=True, force=True)
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    ###########################################################
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None
    yql_query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "') and u='c'"
    ###########################################################
    if yql_query is None:
        return {}
    yql_url = baseurl + urllib.parse.urlencode({'q': yql_query}) + "&format=json"
    result = urllib.request.urlopen(yql_url).read()
    data = json.loads(result)
    ############################################################
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)
    ##############################################################
    res = {"speech": speech,
           "displayText": speech,
           # "data": data,
           # "contextOut": [],
           "source": "apiai-weather-webhook-sample"}
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def searchhook():
    req = request.get_json(silent=True, force=True)
    print("Within Search function......!!")
    baseurl = "https://www.googleapis.com/customsearch/v1?"
    ###########################################################
    result = req.get("result")
    parameters = result.get("parameters")
    search_array = parameters.get("any")
    search_string = str(search_array)
    print(search_string)
    if search_string is None:
        return None
    google_query = "key=AIzaSyDNYsLn4JGIR4UaZMFTAgDB9gKN3rty2aM&cx=003066316917117435589%3Avcms6hy5lxs&q='" + search_string + "'&num=1"
    ###########################################################
    if google_query is None:
        return {}
    #google_url = baseurl + urllib.parse.urlencode({google_query})
    google_url = baseurl + google_query
    print("google_url::::"+google_url)
    result = urllib.request.urlopen(google_url).read()
    data = json.loads(result)
    print("data::::"+data)
    ############################################################
    parsed_input = data.get('query')
    if parsed_input is None:
        return {}

    items = parsed_input.get['items']
    if items is None:
        return {}

    speech = items.get('snippet')

    print("Response:")
    print(speech)
##############################################################
    res = {"speech": speech,
           "displayText": speech,
           # "data": data,
           # "contextOut": [],
           "source": "apiai-seach-webhook-by-swapratim"}
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting APPLICATION on port %d" % port)
    context.run(debug=True, port=port, host='0.0.0.0')
