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
    reqContext = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(reqContext, indent=4))
    print("*******ACTION*******" + reqContext.get("result").get("action"))
    if reqContext.get("result").get("action") == "yahooWeatherForecast":
        #return os.system('python app.py')
		from app import webhook
		res = app.webhook(reqContext)
        print ("Redirection to yahooWeatherForecast")
		
    elif reqContext.get("result").get("action") == "GoogleSearch":
        #return os.system('python search.py')
		res = search.webhook
        print ("Redirection to GoogleSearch")
    else:
        print ("Good Bye")


    # print(res)
    #r = make_response(res)
    #res.headers['Content-Type'] = 'application/json'
    return res


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
