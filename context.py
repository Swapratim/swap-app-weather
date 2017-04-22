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
class Main():
  def webhook():
    reqContext = request.get_json(silent=True, force=True)
    print(json.dumps(reqContext, indent=4))
    if reqContext.get("result").get("action") == "yahooWeatherForecast":
       from Weather import *
       weatherClass = Weather()	
       weatherClass.weatherhook()
    elif reqContext.get("result").get("action") == "GoogleSearch":
       res = search.webhook
       print ("Redirection to GoogleSearch")
    else:
       print ("Good Bye")

class Weather():
  def weatherhook(self):
    req = request.get_json(silent=True, force=True)
    #res = processRequest(req)#################################
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    print ("def processRequest *****" + req.get("result").get("action"))
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    #yql_query = makeYqlQuery(req)
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
    print ("Before hitting makeWebhookResult function")
    #res = makeWebhookResult(data)
    ############################################################
    query = data.get('query')
    print (query)
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
    print ("First res::::")
    print (res)
    res = json.dumps(res, indent=4)
    print("Second res:::")
    print (res)
    r = make_response(res)
    print (r)
    r.headers['Content-Type'] = 'application/json'
    print ("Printing the res::::::::::::")
    print (r)
    return r



#if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting weather on port %d" % port)

    context.run(debug=True, port=port, host='0.0.0.0')
