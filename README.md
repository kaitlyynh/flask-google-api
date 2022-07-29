# flask-google-api

Mainly using Flask and Google Maps API

First: 

from flask import Flask, render_template, url_for, redirect
import googlemaps

You can instantiate a googlemaps client like so:

gmaps = googlemaps.Client(key=API_KEY)
#You need your own API key, access it from the Google cloud platform

In terminal, for MacOS run:
export FLASK_APP=main.py
#the name of your py file
export FLASK_DEBUG=1
#to allow constant updates
flask run
