#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os
#import pgdb
import psycopg2
import urlparse

from flask import Flask
from flask import request, render_template
from flask import make_response


# Flask should start in global layout
context = Flask(__name__)
# Facbook Access Token
ACCESS_TOKEN = "EAAXRzkKCxVQBAImZBQo8kEpHVn0YDSVxRcadEHiMlZAcqSpu5pV7wAkZBKUs0eIZBcX1RmZCEV6cxJzuZAp5NO5ZCcJgZBJu4OPrFpKiAPJ5Hxlve2vrSthfMSZC3GqLnzwwRENQSzZAMyBXFCi1LtLWm9PhYucY88zPT4KEwcZCmhLYAZDZD"
# Google Access Token
Google_Acces_Toekn = "key=AIzaSyDNYsLn4JGIR4UaZMFTAgDB9gKN3rty2aM&cx=003066316917117435589%3Avcms6hy5lxs&q="
# NewsAPI Access Token
newspai_access_token = "505c1506aeb94ba69b72a4dbdce31996"
# Weather Update API KeyError
weather_update_key = "747d84ccfe063ba9"

@context.route('/webhook', methods=['POST'])
# Webhook requests are coming to this method
def webhook():
    reqContext = request.get_json(silent=True, force=True)
    #print(json.dumps(reqContext, indent=4))
    print(reqContext.get("result").get("action"))
    if reqContext.get("result").get("action") == "input.welcome":
       return welcome()
    elif reqContext.get("result").get("action") == "yahooWeatherForecast":
       return weatherhook()
    elif reqContext.get("result").get("action") == "GoogleSearch":
       return searchhook()
    elif reqContext.get("result").get("action") == "DatabaseSearch":
       return dbsearchhook()
    else:
       print("Good Bye")

# This method is to get the username when the user says Hi
def welcome():
    print ("Within Welcome loop")
    data = request.json
    print (data)
    entry = data.get('originalRequest')
    dataall = entry.get('data')
    sender = dataall.get('sender')
    id = sender.get('id')
    fb_info = "https://graph.facebook.com/v2.6/" + id + "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=" + ACCESS_TOKEN
    result = urllib.request.urlopen(fb_info).read()
    #print (result)
    data = json.loads(result)
    first_name = data.get('first_name')
    print (first_name)
    #return "Hi"
    speech = "You can ask about me or weather of any city (like: what's the weather in Copenhagen) or search for an information (like: What is Game Of Thrones?)"
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
    print ("Data.........")
    print (data)
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)
   
# This method is to invoke Yahoo API and process the GET response
def weatherhook():
    req = request.get_json(silent=True, force=True)
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
###########################################################
    result = req.get("result")
    print (result)
    print ('####################')
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if not city:
       city = parameters.get("geo-city-dk")
    print (city)
    print ('********************')
    if city is None:
        return None
    yql_query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "') and u='c'"
###########################################################
    if yql_query is None:
        return {}
    yql_url = baseurl + urllib.parse.urlencode({'q': yql_query}) + "&format=json"
    print (yql_url)
    result = urllib.request.urlopen(yql_url).read()
    data = json.loads(result)
    print (data)
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

    description = item.get('description')
    if description is None:
        return {}

    mytext = "<br />".join(description.split("\n"))
    print (mytext)
    mytext_split_1 = mytext.split('<br />')
    mytext_split_2 = mytext_split_1.split('<BR />')
    print ("@@@@@@@")
    print (mytext_split)

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')
    print(speech)
##############################################################
    res = {"speech": speech,
           "displayText": speech,
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
    search_list0 = parameters.get("any")
    search_u_string_removed = [str(i) for i in search_list0]
    search_list1 = str(search_u_string_removed)
    cumulative_string = search_list1.strip('[]')
    search_string = cumulative_string.replace(" ", "%20")
    print(search_string)
    search_string_ascii = search_string.encode('ascii')
    if search_string_ascii is None:
        return None
    google_query = "key=AIzaSyDNYsLn4JGIR4UaZMFTAgDB9gKN3rty2aM&cx=003066316917117435589%3Avcms6hy5lxs&q=" + search_string_ascii + "&num=1"
###########################################################
    if google_query is None:
        return {}
    #google_url = baseurl + urllib.parse.urlencode({google_query})
    google_url = baseurl + google_query
    print("google_url::::"+google_url)
    result = urllib.request.urlopen(google_url).read()
    print (result)
    data = json.loads(result)
    print ("data = json.loads(result)")
############################################################
    speech = data['items'][0]['snippet'].encode('utf-8').strip()
    #image = data['items'][0]['pagemap'].encode('utf-8').strip()
    #items = data.get('items')
    #if items is None:
    #    return {}
    #x = {"a":3,  "b":4,  "c":5}
      
    #for key in x:   #same thing as using x.keys()
    #  print(key,x[key]) 

    #for value in x.values():
    #  print(value)      #this is better if the keys are irrelevant     

    #for key,value in x.items(): #this gives you both
    #  print(key,value)

    for data_item in data['items']:
        link = data_item['link'],

    for data_item in data['items']:
        pagemap = data_item['pagemap'],

    for key in pagemap:
        cse_thumbnail = key['cse_thumbnail']
        
    if cse_thumbnail is None:
        return {}

    for image_data in cse_thumbnail:
        raw_str = image_data['src'],

    if raw_str is None:
        return {}
    src_u_string_removed = [str(i) for i in raw_str]
    src_u_removed = str(src_u_string_removed)
    src_brace_removed_1 = src_u_removed.strip('[')
    src_brace_removed_2 = src_brace_removed_1.strip(']')
    src_brace_removed_final =  src_brace_removed_2.strip("'")
    # Remove junk charaters from URL
    link_u_removal =  [str(i) for i in link]
    link_u_removed = str(link_u_removal)
    link_brace_removed_1 = link_u_removed.strip('[')
    link_brace_removed_2 = link_brace_removed_1.strip(']')
    link_final =  link_brace_removed_2.strip("'")
    # Remove junk character from search item
    search_string_final = cumulative_string.strip("'")
    print ("Image::::::::")
    print (src_brace_removed_final)
    print ("link_final....")
    print (link_final)
    print("Response:")
    print(speech)
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


def dbsearchhook():
    #r = "Showing the data"
    #print (r)
    conn = psycopg2.connect(database="yousee", user="postgres", password="1234", host="69.195.126.73", port="5432")
    print('connection is successful')
    cur = conn.cursor()
    cur.execute( 'SELECT * FROM yousee;' )
    rows = cur.fetchall()
    for row in rows:
     print ('Customer Name = '), row[1]
     name = row[1]
     #print ("Customer_ID = "), row[0]
     #print ("Customer_Name = "), row[1]
     #print ("Customer_Package = "), row[2]
     #print ("Customer_Status = "), row[3], "\n"
     #print ("Operation done successfully");
    conn.close()
    speech = "Customer Name is " + name
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
