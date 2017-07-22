#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os
import psycopg2
import urlparse

from flask import Flask
from flask import request, render_template
from flask import make_response


# Flask should start in global layout
context = Flask(__name__)
# Facbook Access Token (For Marvin Facebook Page)
ACCESS_TOKEN = "EAAXRzkKCxVQBAImZBQo8kEpHVn0YDSVxRcadEHiMlZAcqSpu5pV7wAkZBKUs0eIZBcX1RmZCEV6cxJzuZAp5NO5ZCcJgZBJu4OPrFpKiAPJ5Hxlve2vrSthfMSZC3GqLnzwwRENQSzZAMyBXFCi1LtLWm9PhYucY88zPT4KEwcZCmhLYAZDZD"
# Facbook Access Token (For SID Facebook Page)
#ACCESS_TOKEN = "EAADCpnCTbUoBAMlgDxoEVTifvyD80zCxvfakHu6m3VjYVdS5VnbIdDnZCxxonXJTK2LBMFemzYo2a4DGrz0SxNJIFkMAsU8WBfRS7IRrZAaHRrXEMBEL5wmdUvzawASQWtZAMNBr90Gattw3IGzeJ7pZBBUthMewXDvnmBELCgZDZD"
# Google Access Token
Google_Acces_Toekn = "key=AIzaSyDNYsLn4JGIR4UaZMFTAgDB9gKN3rty2aM&cx=003066316917117435589%3Avcms6hy5lxs&q="
# NewsAPI Access Token
newspai_access_token = "505c1506aeb94ba69b72a4dbdce31996"
# Weather Update API KeyError
weather_update_key = "747d84ccfe063ba9"

# Webhook requests are coming to this method
@context.route('/webhook', methods=['POST'])
def webhook():
    reqContext = request.get_json(silent=True, force=True)
    if reqContext.get("result").get("action") == "input.welcome":
       return welcome()
    elif reqContext.get("result").get("action") == "yahooWeatherForecast":
       return weatherhook(reqContext)
    elif reqContext.get("result").get("action") == "GoogleSearch":
       return searchhook()
    else:
       print("Good Bye")

# This method is to get the username when the user says Hi
def welcome():
    data = request.json
    if data is None:
        return {}
    entry = data.get('originalRequest')
    dataall = entry.get('data')
    sender = dataall.get('sender')
    id = sender.get('id')
    #print ("id :" + id)
    fb_info = "https://graph.facebook.com/v2.6/" + id + "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=" + ACCESS_TOKEN
    result = urllib.request.urlopen(fb_info).read()
    data = json.loads(result)
    first_name = data.get('first_name')
    speech = "Ask me about: \nWeather of any city (like: how's the weather in Copenhagen) or \nAny topic from Wikipedia (like: What is Game of Throne?)"
    speech2 = "Ask proper questions to get better answers."
    res = {
          "speech": speech,
          "displayText": speech,
           "data" : {
              "facebook" : [
                  {
                 "attachment" : {
                   "type" : "template",
                     "payload" : {
                      "template_type" : "generic",
                       "elements" : [ 
                                 {
                                   "title" : "Hi " + first_name + "! I am Marvin",
                                   "image_url" : "https://pbs.twimg.com/profile_images/717482045019136001/aYzlNG5L.jpg",
                                 } 
                           ]
                       } 
                   }
                },
                 {
                 "text": speech
                  },
                 {
                 "text": speech2
                  }
               ]
             } 
         };
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    
 
# This method is to invoke Yahoo API and process the GET response
#@run_once
def weatherhook(reqContext):
   result = reqContext.get("result")
   parameters = result.get("parameters")
   city = parameters.get("geo-city")
   if not parameters.get("geo-city"):
      city = parameters.get("geo-city-dk")
   ###########################################################
   data = yahoo_weatherapi(city)
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

   link = item.get('link')
   link_forecast = link.split("*",1)[1]
   condition_get_code = condition.get('code')
   condition_code = weather_code(condition_get_code)
   image_url = "http://gdurl.com/" + condition_code
 
   speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
            ", the temperature is " + condition.get('temp') + " " + units.get('temperature')
   res = {
         "speech": speech,
         "displayText": speech,
          "data" : {
             "facebook" : [
                 {
                "text": speech
                 },
                 {
                "attachment" : {
                  "type" : "template",
                    "payload" : {
                     "template_type" : "generic",
                      "elements" : [ 
                                {
                                  "title" : location.get('city') + "-" + location.get('country'),
                                  "image_url" : image_url,
                                  "subtitle" : "",
                                  "buttons": [{
                                       "type": "web_url",
                                       "url": link_forecast,
                                       "title": "Weather Forecast"
                                   }]
                                 } 
                          ]
                      } 
                  }
                }
              ]
            } 
        };
   res = json.dumps(res, indent=4)
   r = make_response(res)
   r.headers['Content-Type'] = 'application/json'
   return r

def yahoo_weatherapi(city):

    yql_query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "') and u='c'"
    if yql_query is None:
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_url = baseurl + urllib.parse.urlencode({'q': yql_query}) + "&format=json"
    result = urllib.request.urlopen(yql_url).read()
    data = json.loads(result)
    return data

def weather_code(condition_get_code):
# Below block of code is to check for weather condition code and map corresponding http://gdurl.com/#### permalink context

    if condition_get_code == "0":
       condition_code = "EmPG"
    elif condition_get_code == "1":
       condition_code = "mh7N"
    elif condition_get_code == "2":
       condition_code = "jENO"
    elif condition_get_code == "3":
       condition_code = "BTT7"
    elif condition_get_code == "4":
       condition_code = "kTWn"
    elif condition_get_code == "5":
       condition_code = "vBIX"
    elif condition_get_code == "6":
       condition_code = "zuxw"
    elif condition_get_code == "7":
       condition_code = "Vy9A"
    elif condition_get_code == "8":
       condition_code = "cT-0"
    elif condition_get_code == "9":
       condition_code = "M4nr"
    elif condition_get_code == "10":
       condition_code = "8-OZ"
    elif condition_get_code == "11":
       condition_code = "4sN0"
    elif condition_get_code == "12":
       condition_code = "SrHt"
    elif condition_get_code == "13":
       condition_code = "i925"
    elif condition_get_code == "14":
       condition_code = "9WKu"
    elif condition_get_code == "15":
       condition_code = "YjI9B"
    elif condition_get_code == "16":
       condition_code = "Lqmw"
    elif condition_get_code == "17":
       condition_code = "8wXj"
    elif condition_get_code == "18":
       condition_code = "AHL1"
    elif condition_get_code == "19":
       condition_code = "pSfX"
    elif condition_get_code == "20":
       condition_code = "ugKj"
    elif condition_get_code == "21":
       condition_code = "eFL0"
    elif condition_get_code == "22":
       condition_code = "Co_g" 
    elif condition_get_code == "23":
       condition_code = "h8uM"
    elif condition_get_code == "24":
       condition_code = "HBlw"
    elif condition_get_code == "25":
       condition_code = "QHzi"
    elif condition_get_code == "26":
       condition_code = "3IaA"
    elif condition_get_code == "27":
       condition_code = "i-dK"
    elif condition_get_code == "28":
       condition_code = "aIAw"
    elif condition_get_code == "29":
       condition_code = "6z8CS"
    elif condition_get_code == "30":
       condition_code = "xt2C"
    elif condition_get_code == "31":
       condition_code = "3Utr"
    elif condition_get_code == "32":
       condition_code = "YHpS"
    elif condition_get_code == "33":
       condition_code = "Hr4W"
    elif condition_get_code == "34":
       condition_code = "84WQ"
    elif condition_get_code == "35":
       condition_code = "3BH6"
    elif condition_get_code == "36":
       condition_code = "vjLN"
    elif condition_get_code == "37":
       condition_code = "41rl"
    elif condition_get_code == "38":
       condition_code = "8Ibx" 
    elif condition_get_code == "39":
       condition_code = "lIee"
    elif condition_get_code == "40":
       condition_code = "9GNz"
    elif condition_get_code == "41":
       condition_code = "uy77"
    elif condition_get_code == "42":
       condition_code = "15Ou"
    elif condition_get_code == "43":
       condition_code = "P_Jg"
    elif condition_get_code == "45":
       condition_code = "wF0D"
    elif condition_get_code == "46":
       condition_code = "1huQ"
    elif condition_get_code == "47":
       condition_code = "MlO5"
    elif condition_get_code == "3200":
       condition_code = "mgzs"
    else: 
       print ("Condition code did not match the sequence")

    return condition_code


# Searchhook is for searching for Wkipedia information via Google API
def searchhook():
    req = request.get_json(silent=True, force=True)
    true_false = True
    baseurl = "https://www.googleapis.com/customsearch/v1?"
###########################################################
    result = req.get("result")
    parameters = result.get("parameters")
    search_list0 = parameters.get("any")
    search_u_string_removed = [str(i) for i in search_list0]
    search_list1 = str(search_u_string_removed)
    cumulative_string = search_list1.strip('[]')
    search_string = cumulative_string.replace(" ", "%20")
    search_string_ascii = search_string.encode('ascii')
    if search_string_ascii is None:
        return None
    google_query = "key=AIzaSyDNYsLn4JGIR4UaZMFTAgDB9gKN3rty2aM&cx=003066316917117435589%3Avcms6hy5lxs&q=" + search_string_ascii + "&num=1"
###########################################################
    if google_query is None:
        return {}
    google_url = baseurl + google_query
    result = urllib.request.urlopen(google_url).read()
    data = json.loads(result)
############################################################
    speech = data['items'][0]['snippet'].encode('utf-8').strip()
    
    for data_item in data['items']:
        link = data_item['link'],

    for data_item in data['items']:
        pagemap = data_item['pagemap'],

    
    cse_thumbnail_u_string_removed = [str(i) for i in pagemap]
    cse_thumbnail_u_removed = str(cse_thumbnail_u_string_removed)
    cse_thumbnail_brace_removed_1 = cse_thumbnail_u_removed.strip('[')
    cse_thumbnail_brace_removed_2 = cse_thumbnail_brace_removed_1.strip(']')
    cse_thumbnail_brace_removed_final =  cse_thumbnail_brace_removed_2.strip("'")
    keys = ('cse_thumbnail', 'metatags', 'cse_image')
    for key in keys:
        true_false = 'cse_thumbnail' in cse_thumbnail_brace_removed_final
        if true_false == True:
            for key in pagemap:
                cse_thumbnail = key['cse_thumbnail']
                for image_data in cse_thumbnail:
                    raw_str = image_data['src']
                    break
        else:
            raw_str = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTwdc3ra_4N2X5G06Rr5-L0QY8Gi6SuhUb3DiSN_M-C_nalZnVA"
            
    src_brace_removed_final = raw_str
    # Remove junk charaters from URL
    link_u_removal =  [str(i) for i in link]
    link_u_removed = str(link_u_removal)
    link_brace_removed_1 = link_u_removed.strip('[')
    link_brace_removed_2 = link_brace_removed_1.strip(']')
    link_final =  link_brace_removed_2.strip("'")
    # Remove junk character from search item
    search_string_final = cumulative_string.strip("'")
    ############################################################
    res = {
          "speech": speech,
          "displayText": speech,
           "data" : {
              "facebook" : [
                  {
                 "attachment" : {
                   "type" : "template",
                     "payload" : {
                      "template_type" : "generic",
                       "elements" : [ 
                                 {
                                   "title" : search_string_final,
                                   "image_url" : src_brace_removed_final,
                                   "subtitle" : "",
                                   "buttons": [{
                                        "type": "web_url",
                                        "url": link_final,
                                        "title": "More info"
                                    }]
                                 } 
                           ]
                       } 
                   }
                },
                 {
                 "text": speech
                  }
               ]
             } 
         };
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting APPLICATION on port %d" % port)
    context.run(debug=True, port=port, host='0.0.0.0')
