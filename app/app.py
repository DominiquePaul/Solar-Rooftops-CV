from flask import Flask, render_template, redirect, url_for, request, Response
from flask import make_response
import os.path
import requests as r
import cv2
from backend.maps_query import gmaps_image
from backend.segmentation import image_segmentation
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
NEWS_API_KEY = '--'
DIFFBOT_TOKEN = '--'

@app.route("/")
def home():
    return "hi"

@app.route("/index")
def index():
    return render_template("index.html", title = 'Solar Rooftops')

@app.route('/run_address', methods=['GET', 'POST'])
def run_address():
    if request.method == 'POST':
        address = request.form['address']

        image = gmaps_image(address)

        retval, buffer = cv2.imencode('.png', image)
        sat_buff = str(base64.b64encode(buffer))[2:-1]

        segmented_image = image_segmentation(image)

        retval, buffer = cv2.imencode('.png', segmented_image)
        seg_buff = str(base64.b64encode(buffer))[2:-1]

        resp = make_response('{"text" : "Looking for address: ' + address + '", "sat_img" : "' + sat_buff + '", "seg_img" : "' + seg_buff + '"}')
        resp.headers['Content-Type'] = "application/json"
        return resp
        #return render_template('index.html', message='')

if __name__ == "__main__":
    app.run(debug = True)