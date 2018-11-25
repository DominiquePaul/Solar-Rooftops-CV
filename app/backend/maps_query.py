import cv2
import urllib.request
from io import BytesIO
import numpy as np
import requests
import math

def gmaps_image(location, zoom=19, size=[300,300]):
    location = location.replace(" ", "+")
    image_url = "https://maps.googleapis.com/maps/api/staticmap?center=" + location + "&zoom=" + str(zoom) + "&size=" + str(size[0]) + "x" + str(size[1]) + "&maptype=satellite&key=AIzaSyCMCczdtg3LgNkbp-vEMLkhtNKjMkdifVI"
    requested_url = urllib.request.urlopen(image_url)
    image_array = np.asarray(bytearray(requested_url.read()), dtype=np.uint8)
    img = cv2.imdecode(image_array, -1)
    return img

def gmaps_area(location, zoom=19, size=[300,300]): 
    location = location.replace(" ", "+")
    response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=" + location + "&key=AIzaSyCMCczdtg3LgNkbp-vEMLkhtNKjMkdifVI")
    resp_json_payload = response.json()
    lat = resp_json_payload['results'][0]['geometry']['location']['lat']
    lon = resp_json_payload['results'][0]['geometry']['location']['lng']
    metersPerPx = 156543.03392 * math.cos(lat*math.pi/180)/math.pow(2,zoom)
    area = size[0]*size[1]*metersPerPx**2
    return area, lat, lon #in meters squared