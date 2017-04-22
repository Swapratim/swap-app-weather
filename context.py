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
    print("*******ACTION*******" + reqContext.get("result").get("action"))
    if reqContext.get("result").get("action") == "yahooWeatherForecast":
        print ("Before going to weather.py")
        from weather import *
        print ("weather imported successfully")
        WeatherObj = weather()
        result = WeatherObj.weatherhook()
        print ("Weather information updated and result assigned to RESULT variable")
        print ("!!!!!!!!!!!" + result)
        return result
		
    elif reqContext.get("result").get("action") == "GoogleSearch":
        #return os.system('python search.py')
        res = search.webhook
        print ("Redirection to GoogleSearch")
    else:
        print ("Good Bye")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting weather on port %d" % port)

    context.run(debug=True, port=port, host='0.0.0.0')
