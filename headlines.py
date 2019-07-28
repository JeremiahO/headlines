import feedparser
import os
import json
import urllib.parse
import urllib.request
import urllib
import datetime

from flask import Flask  # import Flask from the package flask
from flask import render_template
from flask import send_from_directory
from flask import request
from flask import make_response

''' PAGE 75 - Adding Padding to our CSS '''

''' @TO DO:
- Upload website to free Heroku VPS
- Pair this with working on Personal website
- Look into VPS with Raspberry Pi for testing

'''

app = Flask(__name__)  # Cresting and instance of the flask object

RSS_FEED = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': 'http://www.iol.co.za/cmlink/1.640'
            }

DEFAULTS = {'publication': 'bbc',
            'city': 'London,UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'
            }

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&APPID=b6b8600522bd514bdf3a52e51e709692"

CURRENCY_URL = "https://openexchangerates.org/api/latest.json?app_id=57d8e99a00ee40ad9f785ccfb6e531a8"

# A python decorator -- used for URL routing, maing the function below it should be called when the user visits the main page


@app.route("/")
# @app.route("/<publication>")  # Routing Dynamically typed
# ROUTINIG STATICALLY TYPED
# def bbc():
#    return get_news('bbc')
# @app.route("/cnn")
# def cnn():
#    return get_news('cnn')
def home():
    # get customized headlines based on users input or default
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)
    # get customized weather based on users input or default
    city = get_value_with_fallback("city")
    weather = get_weather(city)
    # get customized currency data based on users input or default
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate, currencies = get_rate(currency_from, currency_to)
    # Save cookies and return template
    response = make_response(render_template("home.html", articles=articles, weather=weather,
                                             currency_from=currency_from, currency_to=currency_to,
                                             rate=rate, currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    #response.set_cookie("publication", publication, expires=expires)
    #response.set_cookie("city", city, expires=expires)
    #response.set_cookie("currency_from", currency_from, expires=expires)
    #response.set_cookie("currency_to", currency_to, expires=expires)

    return response


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)


def get_news(publication):  # Simple function that returns a message
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEED:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    # Takes the url parses the feed and creates a python dictionary
    feed = feedparser.parse(RSS_FEED[publication])
    # entries refers to all the feed enties in the dictionary and we took the first one
    # used to access only the first article
    # first_article = feed['entries'][0]
    return feed['entries']


def get_weather(query):
    # print(query)
    # query = urllib.parse.quote(query)
    # print("query with urllib: " + query)
    url = WEATHER_URL.format(query)
    # print("url: " + url)
    data = urllib.request.urlopen(url).read()
    # print(data)
    parsed = json.loads(data)
    # print(parsed)
    weather = None
    if parsed.get('weather'):
        # print('true')
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name']
                   }
    # print(weather)
    return weather


def get_rate(frm, to):
    all_currency = urllib.request.urlopen(CURRENCY_URL).read()

    parsed = json.loads(all_currency).get('rates')
    print(parsed)

    frm_rate = parsed.get(frm)
    print(frm_rate)

    to_rate = parsed.get(to)
    print(to_rate)

    if frm or to == None:
        rate = 0
    else:
        rate = to_rate/frm_rate

    return (rate, parsed.keys())

# This deals with the issues of a requested favicon.ico its code provided in the flask documentation


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':  # used to stop scripts from being unintentionally run
    # It is used to kick off flasks app dev server on a local machine
    app.run()
    # port=8000, debug=True
